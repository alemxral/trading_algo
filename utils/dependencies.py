# dependencies.py

# System & OS Utilities
import os
import sys
import logging
from pathlib import Path

# Data Handling
import numpy as np
import pandas as pd
import scipy.stats as stats
import joblib  # Model serialization

# Machine Learning & Modeling
from sklearn.neighbors import KNeighborsClassifier
import statsmodels.api as sm


# API & Data Fetching
import requests
import yfinance as yf
import ccxt  # Crypto exchange APIs
# Database
import sqlite3
from sqlalchemy import create_engine



# Time Handling
from datetime import datetime, timedelta
import dateutil.parser

# Notifications
import smtplib


# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Scheduling & Automation
import schedule
from apscheduler.schedulers.background import BackgroundScheduler

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
