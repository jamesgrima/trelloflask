FROM python
WORKDIR /teamshandler
COPY . /teamshandler
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "main.py"]
