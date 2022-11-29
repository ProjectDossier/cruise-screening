
Create env for prompt_api:

```
conda create -n cruise_prompts python=3.8.15
```

Activate env:

```
conda activate cruise_prompts
```

Install requirements:

```
pip install -r requirements.txt
conda install pytorch torchvision torchaudio pytorch-cuda=11.6 -c pytorch -c nvidia
```

Run the app:

```
export FLASK_APP=screening_app.py
flask run
```