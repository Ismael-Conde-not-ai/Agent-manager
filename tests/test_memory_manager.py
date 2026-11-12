from memory.memory_manager import MemoryManager


def main():
    memory = MemoryManager()
    memory.remember("Task started")
    memory.remember("Research completed")
    print(memory.get_working_memory())
    memory.clear_working_memory()
    print(memory.get_working_memory())


if __name__ == "__main__":
    main()
