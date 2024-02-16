
FROM public.ecr.aws/lambda/python

COPY function.py requirements.txt ./

RUN python -m pip install -r requirements.txt -t .

CMD ["function.lambda_handler"]