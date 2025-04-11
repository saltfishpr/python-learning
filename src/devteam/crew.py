import os
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

local_gemini = LLM(
    model="ollama/gemma3:27b",
    base_url="http://localhost:11434",
)

gemini = LLM(
    model="gemini/gemini-2.0-flash",
)


@CrewBase
class Devteam:
    """Devteam crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def product_owner(self) -> Agent:
        return Agent(
            config=self.agents_config["product_owner"], llm=gemini, verbose=True
        )

    @agent
    def system_architect(self) -> Agent:
        return Agent(config=self.agents_config["system_architect"], verbose=True)

    @agent
    def developer(self) -> Agent:
        return Agent(config=self.agents_config["developer"], verbose=True)

    @agent
    def qa(self) -> Agent:
        return Agent(config=self.agents_config["qa"], verbose=True)

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def define_product_vision(self) -> Task:
        return Task(
            config=self.tasks_config["define_product_vision"],
        )

    @task
    def manage_product_backlog(self) -> Task:
        return Task(
            config=self.tasks_config["manage_product_backlog"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Devteam crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=Agent(
                config=self.agents_config["scrum_master"],
                llm=gemini,
                verbose=True,
            ),
            verbose=True,
        )
