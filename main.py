from dotenv import load_dotenv
from omegaconf import OmegaConf
from llm import LLMWorker

load_dotenv()

dialog = ""
config = OmegaConf.load('config.yaml')
llm_worker = LLMWorker(config=config)
print(llm_worker.extract_tasks(dialog))