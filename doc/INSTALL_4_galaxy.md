# SETUP dependency

## Install ansible and git

* sudo apt-get install git ansible

 ansible > 2.9.27 

## Fetch Prepmetvet repository

* git clone **url_to_prepmetvet_repository**

# INSTALL GALAXY
Install galaxy with ansible one line command.

* `cd Prepmetvet_analyses/galaxy`
* `ansible-playbook galaxy_server.yml -u admin -K `` where admin is a sudo user, depends on your settings.


# SETUP GALAXY

## API KEY 
* Connect to the galaxy instance with a web browser : http://localhost for next steps, this element will be called IP_GALAXY
* Create a user, use your email to register.
* Go to settings account and create a API key (copy it) for next steps, this element will be called API_GALAXY

## Install tools and workflow

### Install Ephemeris environment

Be sure not to be in a conda environment by typing  ```conda deactivate``` in your terminal, then _Enter_ key.

Create a virtualenv environment (with pip)

**PATH_PREPMEDVET** is full path where you clone git repository (ex /home/admin/PrepMedVet_Analyses)
``` 
virtualenv env 
source env/bin/activate
pip install -r PATH_PREPMEDVET/galaxy/tools_workflows_requirements/txt
``` 
       

### Install tools and after workfow

You have 1 script in each directory  PATH_PREPMEDVET/galaxy_workflow/install_Y  (Y=1,2,3)

You have to launch them in increasing order, 1, 2, 3 as described bellow:

```
sh PATH_PREPMEDVET/galaxy_workflow/install_1/workflow-and-tools-install.sh IP  API_GALAXY
sh PATH_PREPMEDVET/galaxy_workflow/install_2/workflow-and-tools-install.sh IP  API_GALAXY
sh PATH_PREPMEDVET/galaxy_workflow/install_3/workflow-and-tools-install.sh IP  API_GALAXY
```

###



