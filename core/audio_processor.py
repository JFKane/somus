import asyncio
import logging
from typing import Dict, Any, Callable, List
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        self.tasks = {}

    async def process_audio(self, config: Dict[str, Any], task_id: str, update_callback: Callable):
        logger.info(f"Starting audio processing task: {task_id}")
        self.tasks[task_id] = {
            "status": "running",
            "config": config,
            "results": []
        }

        try:
            audio_resource = config['audio_resource']
            if isinstance(audio_resource, dict):
                if audio_resource['type'] == 'local_file':
                    audio_path = audio_resource['path']
                    audio, sample_rate = librosa.load(audio_path, sr=config.get('sample_rate', 44100))
                else:
                    raise ValueError(f"Unsupported audio resource type: {audio_resource['type']}")
            else:
                # Assume it's a URL if it's a string
                audio_path = audio_resource
                audio, sample_rate = librosa.load(audio_path, sr=config.get('sample_rate', 44100))

            chunk_size = config.get('chunk_size', 1024)
            frequency = config.get('frequency', 1)

            for i in range(0, len(audio), chunk_size):
                chunk = audio[i:i+chunk_size]
                await self.process_chunk(chunk, config['plugins'], task_id, update_callback)
                await asyncio.sleep(frequency)

        except Exception as e:
            logger.error(f"Error in audio processing task {task_id}: {str(e)}")
            self.tasks[task_id]["status"] = "error"
        else:
            self.tasks[task_id]["status"] = "completed"

        logger.info(f"Audio processing task completed: {task_id}")

    async def process_chunk(self, audio_chunk: np.ndarray, plugins: List[Dict[str, Any]], task_id: str, update_callback: Callable):
        results = {}
        for plugin_config in plugins:
            plugin_name = plugin_config['name']
            plugin_params = plugin_config.get('params', {})
            plugin = self.plugin_manager.get_plugin(plugin_name)
            if plugin:
                try:
                    result = plugin['function'](audio_chunk, **plugin_params)
                    results[plugin_name] = result
                except Exception as e:
                    logger.error(f"Error in plugin {plugin_name}: {str(e)}")
                    results[plugin_name] = {"error": str(e)}
            else:
                logger.warning(f"Plugin not found: {plugin_name}")

        self.tasks[task_id]["results"].append(results)
        await update_callback({"task_id": task_id, "results": results})

    def stop_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "stopped"
            return True
        return False

    def get_task_status(self, task_id: str) -> str:
        return self.tasks.get(task_id, {}).get("status")

    def get_report(self, task_id: str) -> Dict[str, Any]:
        return self.tasks.get(task_id)