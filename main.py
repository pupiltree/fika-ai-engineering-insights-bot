from agents.data_harvester import DataHarvesterAgent

if __name__ == "__main__":
    agent = DataHarvesterAgent()
    events = agent.invoke()
    print(events)
