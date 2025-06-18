.PHONY: default test

include .env
export 


src=src
dist=dist
target=dist/target.zip

default: # noop
	@echo "dev: $(DEV_FN)" \
	&& echo "prd: $(PRD_FN)"

identity: # configure aws user
	aws sts get-caller-identity

test:
	clear && python -m pytest -vs

test-ssm:
	clear && python -m pytest -vs test_ssm.py

test-lambda:
	clear && python -m pytest -vs test_lambda.py

prepare:
	git rev-parse HEAD > src/commit.txt \
	&& mkdir -p $(dist) \
	&& rm -f $(target) \
	&& (cd $(src) && zip -r ../$(target) . -x ".*" "__pycache__/*" "venv/*") 

dev-deploy:
	make prepare \
	&& aws lambda update-function-code --function-name $(DEV_FN) --zip-file fileb://$(target) --no-cli-pager \
	&& sleep 5 \
	&& aws lambda update-function-configuration --function-name $(DEV_FN) --environment Variables='{ENVIRONMENT=dev}' 

prd-deploy:
	make prepare \
	&& aws lambda update-function-code --function-name $(PRD_FN) --zip-file fileb://$(target) --no-cli-pager \
	&& sleep 5 \
	&& aws lambda update-function-configuration --function-name $(PRD_FN) --environment Variables='{ENVIRONMEN=prd}'



