import logging
import os

from bs4 import BeautifulSoup, NavigableString
from pydantic import BaseModel

from translate import translate_text

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",  # noqa: E501
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class IniFlag(BaseModel):
    category: str
    filename: str
    section: str
    key: str
    value_type: str
    default_value: str
    adds_to_list: str

    desc: str | None = None


def load_ini_flags(filename: str, category: str) -> list[IniFlag]:
    import csv

    ini_flags: list[IniFlag] = []
    with open(filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            ini_flag = IniFlag(
                category=category,
                filename=row[0],
                section=row[1],
                key=row[2],
                value_type=row[3],
                default_value=row[4],
                adds_to_list=row[5],
            )
            if ini_flag.key == "":
                continue
            ini_flags.append(ini_flag)
    return ini_flags


def load_all_ini_flags(dir: str) -> list[IniFlag]:
    ini_flags = []
    for filename in os.listdir(dir):
        if filename.endswith(".csv"):
            ini_flags += load_ini_flags(
                os.path.join(dir, filename), filename.removesuffix(".csv")
            )
    return ini_flags


def load_modenc_data(data_dir: str) -> dict[str, str]:
    """加载 data_dir 中的所有 html 文件"""
    dir = os.path.join(data_dir, "modenc")

    html_files = {}
    for filename in os.listdir(dir):
        if filename.startswith("index.php"):
            continue
        if filename.endswith(".html"):
            filepath = os.path.join(dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    html_files[filename.removesuffix(".html")] = f.read()
                logger.debug(f"Loaded HTML file: {filename}")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {str(e)}")

    return html_files


def extract_description(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    root = soup.find(id="mw-content-text")
    flag = root.find("br", attrs={"clear": "all"})
    if not flag:
        return ""

    found = False
    desc_parts = []
    for element in flag.parent.contents:
        if element == flag:
            found = True
            continue
        if not found:
            continue

        if isinstance(element, NavigableString):
            desc_parts.append(str(element).strip())
        else:
            text = element.get_text(separator=" ", strip=True)
            if text:
                desc_parts.append(text)
            if element.name not in ["span", "a", "b", "i"]:
                desc_parts.append("\n")
    return " ".join(desc_parts).strip()


def try_translate_text(
    text: str,
    source_language_code: str = "en",
    target_language_code: str = "zh",
) -> str:
    try:
        return translate_text(text, source_language_code, target_language_code)
    except Exception:
        logger.exception(f"translate {text} to {target_language_code}")
        return ""


class IniSchema(BaseModel):
    version: str = ""
    flags: list[IniFlag] = []

    def get_flag(self, filename: str, section: str, key: str) -> IniFlag | None:
        for flag in self.flags:
            if (
                flag.filename == filename
                and flag.section == section
                and flag.key == key
            ):
                return flag
        return None


def main(data_dir: str, target_language_codes: list[str]):
    ini_flags = load_all_ini_flags(data_dir)
    output_path = os.path.join(data_dir, "schema.json")

    modenc_data = load_modenc_data(data_dir)

    schema = IniSchema()
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                schema = IniSchema.model_validate_json(f.read())
        except Exception:
            logger.exception(f"load {output_path} to schema")

    for ini_flag in ini_flags:
        flag = schema.get_flag(ini_flag.filename, ini_flag.section, ini_flag.key)
        if flag is None:
            flag = ini_flag
            schema.flags.append(flag)

        if flag.key not in modenc_data:
            logger.warning(f"{flag.key} not found in modenc_data")
            continue
        html = modenc_data[flag.key]
        flag.desc = extract_description(html)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(schema.model_dump_json(indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help="Path to data folder")
    target_language_codes = ["zh"]
    args = parser.parse_args()

    main(args.data_dir, target_language_codes)
