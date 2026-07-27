FROM python:3.14.6-alpine3.23 AS build
ADD . /baby-world-home-page
WORKDIR /baby-world-home-page
RUN pip install --prefix/install -r /baby-world-home-page/requirements.txt

FROM python:3.14.6-alpine3.23 AS runtime
COPY --from=build /install /usr/local
COPY --from=build /baby-world-home-age /baby-world-home-age
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]