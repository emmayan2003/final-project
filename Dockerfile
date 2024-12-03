FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 77 78 79

CMD ["python", "./Server.py", "0.0.0.0", "5777", "5778", "5779", "5", "3"]