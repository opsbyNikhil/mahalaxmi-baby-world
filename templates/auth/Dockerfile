FROM python:3.12.12-alpine AS build
ADD . /Baby-World-Auth
WORKDIR /Baby-World-Auth
RUN pip install --prefix=/install /Baby-World-Auth/requirements.txt

FROM python:3.12.12-alpine AS runtime
WORKDIR /Baby-World-Auth
COPY --from=build /install /usr/local
COPY --from=build /Baby-World-Auth /Baby-World-Auth
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
