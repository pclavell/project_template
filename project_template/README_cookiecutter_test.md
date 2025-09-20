Progress and testing for cookiecutter-ifying the template


* Goal : global imports which enable whatever directory structure you want

 this works!!
```bash
cookiecutter project_template --no-input
```

does not work
<!-- Let's try now to recursively run this to create new users
```bash
cookiecutter project_template \
  --no-input \
  project_name='test_cookiecutter' # hopefully this comb. of args will only fill in project name for now
``` -->

I will now try with user: {{cookiecutter.user}} in the replacement LOL
```bash
cookiecutter project_template --no-input
```
