from ..worker_manager import WorkerManager

def start_workers(count):
    """Start worker processes"""
    manager = WorkerManager()
    manager.start_workers(count)

def stop_workers():
    """Stop worker processes"""
    manager = WorkerManager()
    manager.stop_workers()
