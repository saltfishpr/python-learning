import typing_extensions
import autogen

from autogen_demo import dice

local_llm_config = {
    "config_list": [
        {
            "model": "llama3.1:8b-chinese",  # Loaded with LiteLLM command
            "api_key": "NotRequired",  # Not needed
            "base_url": "http://localhost:11434/v1",  # Your LiteLLM URL
            "price": [0, 0],  # Put in price per 1K tokens [prompt, response] as free!
        }
    ],
    "cache_seed": None,
}

system_message = """
你的名字是 Cathy，你是一名 dungeon master。我们现在正在玩 Dungeons and Dragons 5E。
你负责这场游戏，你了解所有角色。
只有你知道这个故事。
不要试图提前结束这次会话，我们还有几个小时，不想让玩家们感到失望。
如果玩家们想要做些什么，你可以让他们掷骰子来决定。
然后你可以根据掷出的结果和难度等级来判断结果。对于简单任务使用10，中等任务使用15，困难任务使用20。
"""
dm = autogen.AssistantAgent(
    name="cathy",
    description="Cathy 是一名 dungeon master。她正在主持这场游戏。她可以要求玩家为行动掷骰子，并且她知道整个故事。她负责掌控全局。",
    system_message=system_message,
    llm_config=local_llm_config,
    human_input_mode="NEVER",
)
diceroller = autogen.AssistantAgent(
    name="diceroller",
    description="掷特定数量的多面骰子，你可以决定骰子的面数。返回一个数字。",
    llm_config=local_llm_config,
    code_execution_config={
        "use_docker": False,
    },
)

player1 = autogen.AssistantAgent(
    name="joe",
    system_message="你的名字是 Joe，你是一名兽人狂战士。你高大、强壮，但不太聪明。你不擅长交谈，但你很擅长战斗。你对朋友忠诚，总是准备投入战斗。",
    llm_config=local_llm_config,
    human_input_mode="NEVER",  # Never ask for human input.
    max_consecutive_auto_reply=1,
)
player2 = autogen.AssistantAgent(
    name="matt",
    system_message="你的名字是 Matt，你是一名人类吟游诗人。你口才流利，唱歌也很好听。你不擅长战斗，但你很擅长交谈。你对朋友忠诚，总是准备通过交谈来避免战斗。",
    llm_config=local_llm_config,
    human_input_mode="NEVER",  # Never ask for human input.
    max_consecutive_auto_reply=1,
)

human_player = autogen.UserProxyAgent(
    name="kate",
    system_message="你的名字是 Kate，你是一名人类巫师。你不擅长肉搏战斗，但你精通魔法。你对朋友忠诚，总是准备施展法术。",
    human_input_mode="ALWAYS",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "temp",
        "use_docker": False,
    },
)

group_chat = autogen.GroupChat(
    agents=[dm, player1, player2, human_player],
    messages=[],
    max_round=160,
    send_introductions=True,
)
group_chat_manager = autogen.GroupChatManager(
    groupchat=group_chat, llm_config=local_llm_config
)

chat_result = dm.initiate_chat(
    group_chat_manager,
    message="欢迎来到我们的第一次游戏会话。像所有美好的冒险一样，我们从一家酒馆开始。你们都坐在酒馆角落的一张桌子旁。酒馆里挤满了人，酒保忙碌不已。你们想做什么？",
    summary_method="reflection_with_llm",
)


@dm.register_for_execution()
@player1.register_for_execution()
@player2.register_for_execution()
@human_player.register_for_execution()
@diceroller.register_for_llm(
    description="掷特定数量的多面骰子，你可以决定骰子的面数。返回一个数字。",
)
def dice_roller(
    number: typing_extensions.Annotated[int, "how many dice you want to roll"],
    sides: typing_extensions.Annotated[int, "how many sides the dice have"],
) -> str:
    result = dice.roll(int(number), int(sides))
    print(result)
    return f"{result}"
