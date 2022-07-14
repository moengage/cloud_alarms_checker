# How to add any new resource in AWS

1. In [constants.py](utils/constants.py), add the new resource name in `ResourceType`  class

2. In [constants.py](utils/constants.py), add the new cloudwatch metric if required in `CloudwatchMetric` class

3. Map the resource name and cloud watch metrics in `MANDATORY_ALARM_METRICS` and `METRIC_RESOURCE_TYPE_MAP` maps, present in[constants.py](utils/constants.py)

4. Create a new resource class by taking the example from any existing resource class, or from [template.py](./template.py)

5. Import the new class created in [aws_main.py](../aws_main.py)  
    `For ex- from cloud.aws.resource_classes.elasticache_redis import ElasticacheRedisAWSResource`

6. Import the new class created in [__init.py__](./__init__.py)  
    `For ex - from cloud.aws.resource_classes.elasticache_redis import ElasticacheRedisAWSResource`

7. Add the new class in `resource_classes` variable in [aws_main.py](../aws_main.py)