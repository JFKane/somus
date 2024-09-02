import asyncio
import logging
from typing import Dict, Any, Callable, List 
import numpy as np
import sounddevice as sd

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
            # This is a placeholder for actual audio processing
            # In a real implementation, you'd handle different audio sources (file, stream, etc.)
            sample_rate = config.get('sample_rate', 44100)
            chunk_size = config.get('chunk_size', 1024)
            duration = 10  # Process 10 seconds of audio for this example

            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                audio_chunk = indata.copy()
                asyncio.create_task(self.process_chunk(audio_chunk, config['plugins'], task_id, update_callback))

            with sd.InputStream(samplerate=sample_rate, channels=1, callback=audio_callback, blocksize=chunk_size):
                await asyncio.sleep(duration)

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