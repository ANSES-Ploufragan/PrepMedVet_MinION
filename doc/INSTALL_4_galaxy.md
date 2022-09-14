# SETUP dependency

## Install ansible and git

* sudo apt-get install git ansible

 ansible > 2.9.27 

## Fetch Prepmetvet repository

* git clone **url_to_prepmetvet_repositoty**

# INSTALL GALAXY
Install galaxy with ansible one line command.

* `cd Prepmetvet_analyses/galaxy`
* `ansible-playbook galaxy_server.yml -u admin -K `` where admin is a sudo user, depend on your settings.


# SETUP GALAXY

## API KEY 
* Connect to  galaxy instance with a navigateur : http://localhost
* Create a user, use your email to register.
* Go to settings account and create a API key (copy it)

## Install tools and workflow


TODO :  test
       
return in directory Prepmetvet galaxy
* change API key in files tools.yaml and worflow.yaml

execute command line

* ``ansible-playbook tools.yaml -u admin -K `` 
* ``ansible-playbook workflow.yaml -u admin -K `` 


* TODO : create a var fil with api key and put var api_key in tools.yaml workflow.yaml


* TODO : Find a best way for create list of tools with version and updated workflow

