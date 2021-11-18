FROM python:3.9

ENV PYTHONUNBUFFERED 1

ARG PROJECT_DIR="/config"

COPY . ${PROJECT_DIR}

WORKDIR ${PROJECT_DIR}
# WORKDIR /web

# pip upgrade
RUN pip install --upgrade pip

# RUN brew install pyenv
# RUN brew install pyenv-virtualenv

# pyenv settings
# ENV PATH /root/.pyenv/bin:$PATH
# RUN echo 'export PYENV_ROOT=/usr/local/var/pyenv' >> ~/.zshrc
# RUN echo 'eval if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi' >> ~/.zshrc
# RUN echo 'eval if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi' >> ~/.zshrc
# RUN source ~/.zshrc

# RUN pyenv install 3.9.5

# pyenv virtualenv
# RUN pyenv virtualenv 3.9.5 fbv_drf
# RUN pyenv local fbv_drf

# requirements install
RUN pip install -r requirements.txt

# RUN mkdir -p static
# RUN python manage.py collectstatic --noinput

# CMD python manage.py runserver 0.0.0.0:8000 --settings=config.settings.local

# EXPOSE 8000