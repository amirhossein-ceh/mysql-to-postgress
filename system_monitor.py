import psutil
import threading
import time
import gc
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

class SystemMonitor:
    """System resource monitoring and management"""
    
    def __init__(self, max_memory_mb: int = 1024, cpu_cores: int = 3):
        self.max_memory_mb = max_memory_mb
        self.cpu_cores = min(cpu_cores, mp.cpu_count())
        self.memory_usage_history = []
        self.cpu_usage_history = []
        self.monitoring = False
        self.monitor_thread = None
        self.executor = None
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory usage information"""
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            'total_memory_mb': round(memory.total / (1024 * 1024), 2),
            'available_memory_mb': round(memory.available / (1024 * 1024), 2),
            'used_memory_mb': round(memory.used / (1024 * 1024), 2),
            'memory_percent': memory.percent,
            'process_memory_mb': round(process_memory.rss / (1024 * 1024), 2),
            'process_memory_percent': round((process_memory.rss / memory.total) * 100, 2),
            'max_memory_limit_mb': self.max_memory_mb,
            'memory_warning': process_memory.rss / (1024 * 1024) > self.max_memory_mb * 0.8
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get current CPU usage information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'cpu_cores_used': self.cpu_cores,
            'cpu_frequency_mhz': cpu_freq.current if cpu_freq else 0,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        memory_info = self.get_memory_info()
        cpu_info = self.get_cpu_info()
        
        return {
            'memory': memory_info,
            'cpu': cpu_info,
            'timestamp': time.time()
        }
    
    def start_monitoring(self, interval: float = 2.0):
        """Start continuous system monitoring"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Internal monitoring loop"""
        while self.monitoring:
            try:
                system_info = self.get_system_info()
                
                # Store history (keep last 50 entries)
                self.memory_usage_history.append(system_info['memory'])
                self.cpu_usage_history.append(system_info['cpu'])
                
                if len(self.memory_usage_history) > 50:
                    self.memory_usage_history.pop(0)
                if len(self.cpu_usage_history) > 50:
                    self.cpu_usage_history.pop(0)
                
                # Check memory limits and trigger garbage collection if needed
                if system_info['memory']['memory_warning']:
                    self._handle_memory_pressure()
                
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _handle_memory_pressure(self):
        """Handle memory pressure by triggering garbage collection"""
        print("Memory pressure detected, triggering garbage collection...")
        gc.collect()
    
    def create_executor(self, use_processes: bool = False) -> ThreadPoolExecutor:
        """Create a thread/process pool executor with configured CPU cores"""
        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=self.cpu_cores)
        else:
            self.executor = ThreadPoolExecutor(max_workers=self.cpu_cores)
        return self.executor
    
    def cleanup_executor(self):
        """Clean up the executor"""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
    
    def set_cpu_cores(self, cores: int):
        """Update the number of CPU cores to use"""
        self.cpu_cores = min(cores, mp.cpu_count())
        print(f"CPU cores set to: {self.cpu_cores}")
    
    def set_memory_limit(self, memory_mb: int):
        """Update the memory limit in MB"""
        self.max_memory_mb = memory_mb
        print(f"Memory limit set to: {self.max_memory_mb} MB")
    
    def get_memory_history(self) -> list:
        """Get memory usage history"""
        return self.memory_usage_history.copy()
    
    def get_cpu_history(self) -> list:
        """Get CPU usage history"""
        return self.cpu_usage_history.copy()
    
    def force_garbage_collection(self):
        """Manually trigger garbage collection"""
        collected = gc.collect()
        print(f"Garbage collection freed {collected} objects")
        return collected

class MemoryController:
    """Memory usage controller for database operations"""
    
    def __init__(self, system_monitor: SystemMonitor):
        self.system_monitor = system_monitor
        self.batch_size = 1000
        self.max_batch_size = 10000
        self.min_batch_size = 100
    
    def get_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on current memory usage"""
        memory_info = self.system_monitor.get_memory_info()
        
        # If memory usage is high, reduce batch size
        if memory_info['memory_warning']:
            self.batch_size = max(self.min_batch_size, self.batch_size // 2)
        # If memory usage is low, we can increase batch size
        elif memory_info['memory_percent'] < 50:
            self.batch_size = min(self.max_batch_size, self.batch_size * 2)
        
        return self.batch_size
    
    def should_pause_processing(self) -> bool:
        """Check if processing should be paused due to memory pressure"""
        memory_info = self.system_monitor.get_memory_info()
        return memory_info['memory_warning'] and memory_info['memory_percent'] > 85
    
    def pause_for_memory_recovery(self, duration: float = 1.0):
        """Pause processing to allow memory recovery"""
        if self.should_pause_processing():
            print(f"Pausing for {duration} seconds due to memory pressure...")
            time.sleep(duration)
            self.system_monitor.force_garbage_collection()
