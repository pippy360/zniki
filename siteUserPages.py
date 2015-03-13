from database import databaseFunctions
import redis
import filesAPI
import thumbnailGenerator
from flask import Flask, render_template, request, send_file, redirect, url_for
from flask.ext import login
import loginLogic
import utils
from app import app, login