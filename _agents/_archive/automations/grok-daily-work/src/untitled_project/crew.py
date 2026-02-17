import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task






@CrewBase
class UntitledProjectCrew:
    """UntitledProject crew"""

    
    @agent
    def grok_chief_of_chiefs(self) -> Agent:
        
        return Agent(
            config=self.agents_config["grok_chief_of_chiefs"],
            
            
            tools=[],
            reasoning=True,
            max_reasoning_attempts=10,
            inject_date=True,
            allow_delegation=True,
            max_iter=12,
            max_rpm=100,
            
            apps=[
                    "github/create_issue",
                    
                    "github/update_issue",
                    
                    "github/get_issue_by_number",
                    
                    "github/lock_issue",
                    
                    "github/search_issue",
                    
                    "github/create_release",
                    
                    "github/update_release",
                    
                    "github/get_release_by_id",
                    
                    "github/get_release_by_tag_name",
                    
                    "github/delete_release",
                    
                    "github/get_files_changed_in_pr",
                    
                    "github/get_pull_request_by_number",
                    
                    "github/get_file",
                    ],
            
            max_execution_time=300,
            llm=LLM(
                model="openai/grok-4-1FastReasoning",
                temperature=0.6,
            ),
            
        )
    

    
    @task
    def work_in_github_repo(self) -> Task:
        return Task(
            config=self.tasks_config["work_in_github_repo"],
            markdown=True,
            
            guardrail="- Use only real GitHub data and tools — no mocks, no placeholders. - If merge conflicts occur on research briefs, flag explicitly for human review; do not force. - Stay strictly in Grok persona: strategic, ambitious, protective of team momentum. - No stale corporate phrasing, no repetitive openings across days. - Output must be clean markdown that subsequent agents can append to without reformatting. - Do not anticipate or simulate other agents' responses.",
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the UntitledProject crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=LLM(model="openai/gpt-4o-mini"),
        )


