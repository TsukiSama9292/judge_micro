import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional

import uvicorn
from judge_micro.config.settings import setting


class APIRunner:
    """Judge Micro API Runner"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
    def check_environment(self) -> bool:
        """Check runtime environment"""
        print("🔍 Checking runtime environment...")
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], 
                         capture_output=True, check=True)
            subprocess.run(["docker", "info"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker is not installed or service is not running")
            return False
            
        print("✅ Environment check passed")
        return True
            
    def start_development(self, host: str = None, port: int = None) -> None:
        """Start development server (Uvicorn with reload)"""
        print("🚀 Starting development server (Uvicorn with reload)...")
        
        # Use setting defaults if not provided
        if host is None:
            host = setting.JUDGE_HOST
        if port is None:
            port = setting.JUDGE_PORT
        
        # Set environment variable for debug mode
        os.environ['JUDGE_IS_DEBUG'] = 'true'
        
        uvicorn.run(
            "judge_micro.api.main:get_app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=["src"],
            log_level=setting.JUDGE_LOG_LEVEL.lower(),
            access_log=True,
            use_colors=True,
            factory=True,
        )
    
    def start_production(self, 
                        host: str = None, 
                        port: int = None,
                        workers: Optional[int] = None) -> None:
        """Start production server (Gunicorn with Uvicorn workers)"""
        print("🚀 Starting production server (Gunicorn + Uvicorn workers)...")
        
        # Use setting defaults if not provided
        if host is None:
            host = setting.JUDGE_HOST
        if port is None:
            port = setting.JUDGE_PORT
        
        # Set environment variable for production mode
        os.environ['JUDGE_IS_DEBUG'] = 'false'
        
        if workers is None:
            workers = setting.JUDGE_WORKERS
            
        print(f"📊 Using {workers} workers")
        
        # Build Gunicorn command with all configuration parameters
        cmd = [
            "gunicorn",
            "judge_micro.api.main:get_app()",
            # Worker configuration
            "--worker-class", "uvicorn.workers.UvicornWorker",
            "--workers", str(workers),
            "--worker-connections", "1000",
            # Server socket
            "--bind", f"{host}:{port}",
            "--backlog", "2048",
            # Timeout settings
            "--timeout", "120",
            "--keep-alive", "30",
            "--graceful-timeout", "30",
            # Request limits
            "--max-requests", "1000",
            "--max-requests-jitter", "50",
            "--limit-request-line", "8192",
            "--limit-request-fields", "100",
            # Process settings
            "--preload",
            # Logging configuration (防止重複日誌錯誤)
            "--log-level", setting.JUDGE_LOG_LEVEL.lower(),
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--capture-output",
            "--enable-stdio-inheritance",
            "--access-logformat", '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        ]
            
        try:
            # 使用 Popen 來更好地控制進程
            process = subprocess.Popen(cmd)
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  Server stopping gracefully...")
            try:
                # 給進程一些時間來正常關閉
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 如果進程沒有在 5 秒內關閉，強制終止
                process.kill()
                process.wait()
            except Exception:
                # 忽略關閉過程中的異常，避免重複日誌錯誤
                pass
            print("⏹️  Server stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Startup failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Judge Micro API Entry Point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python3 main.py dev                   # Development mode
  python3 main.py prod                  # Production mode (Gunicorn)
  python3 main.py dev --port 8080       # Custom port
  python3 main.py prod --workers 4      # Custom worker count
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["dev", "prod"],
        help="Startup mode"
    )
    
    parser.add_argument(
        "--host",
        default=setting.JUDGE_HOST,
        help=f"Bind host (default: {setting.JUDGE_HOST})"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=setting.JUDGE_PORT,
        help=f"Bind port (default: {setting.JUDGE_PORT})"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        help="Worker process count (for prod mode only)"
    )
    
    parser.add_argument(
        "--no-check",
        action="store_true",
        help="Skip environment check"
    )
    
    return parser


def main() -> None:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    runner = APIRunner()
    
    # Environment check
    if not args.no_check and not runner.check_environment():
        sys.exit(1)
    
    # Start based on mode
    try:
        if args.mode == "dev":
            runner.start_development(args.host, args.port)
        elif args.mode == "prod":
            runner.start_production(args.host, args.port, args.workers)
    except KeyboardInterrupt:
        print("\n👋 Service stopped")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
