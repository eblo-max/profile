#!/usr/bin/env python3
"""
Setup script for installing Playwright browser on Railway deployment
"""

import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_playwright_browser():
    """Install Playwright Chromium browser"""
    try:
        logger.info("🎭 Starting Playwright browser installation...")
        
        # Set environment variables for Railway/container deployment
        env = os.environ.copy()
        env['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/playwright-browsers'
        env['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '0'
        
        # Install Chromium browser
        logger.info("📦 Installing Chromium browser...")
        result = subprocess.run([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ], env=env, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            logger.info("✅ Playwright Chromium installed successfully!")
            logger.info(f"📄 Installation output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ Failed to install Playwright browser")
            logger.error(f"📄 Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("⏰ Playwright installation timed out")
        return False
    except Exception as e:
        logger.error(f"💥 Error during Playwright installation: {e}")
        return False

def verify_installation():
    """Verify Playwright browser installation"""
    try:
        logger.info("🔍 Verifying Playwright installation...")
        
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if browser_path and os.path.exists(browser_path):
                logger.info(f"✅ Playwright Chromium verified at: {browser_path}")
                return True
            else:
                logger.error("❌ Playwright Chromium not found after installation")
                return False
                
    except ImportError:
        logger.error("❌ Playwright not installed")
        return False
    except Exception as e:
        logger.error(f"❌ Error verifying Playwright: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Railway Playwright setup...")
    
    # Check if we're on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚂 Running on Railway environment")
    else:
        logger.info("💻 Running in local/development environment")
    
    # Install browser
    if install_playwright_browser():
        if verify_installation():
            logger.info("🎉 Playwright setup completed successfully!")
            return 0
        else:
            logger.error("💥 Playwright verification failed")
            return 1
    else:
        logger.error("💥 Playwright installation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 