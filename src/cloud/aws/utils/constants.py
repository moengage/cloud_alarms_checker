# The name of the resources which needs to be monitored.
class ResourceType:
    LOAD_BALANCER = 'LoadBalancer'
    TARGET_GROUP = 'TargetGroup'
    REDIS_CACHE_CLUSTER = 'CacheClusterId'
    SQS_QUEUE = 'QueueName'

# Name of cloudwatch metric.
class CloudwatchMetric:
    HTTPCode_ELB_5XX_Count = 'HTTPCode_ELB_5XX_Count'
    HTTPCode_Target_5XX_Count = 'HTTPCode_Target_5XX_Count'
    TargetResponseTime = 'TargetResponseTime'
    FreeableMemory = 'FreeableMemory'

    EngineCPUUtilization = 'EngineCPUUtilization'
    CPUUtilization = 'CPUUtilization'
    DatabaseMemoryUsagePercentage = 'DatabaseMemoryUsagePercentage'
    NewConnections = 'NewConnections'
    NetworkConntrackAllowanceExceeded ='NetworkConntrackAllowanceExceeded'
    IsMaster = 'IsMaster'
    
    HealthyHostCount = 'HealthyHostCount'
    ApproximateAgeOfOldestMessage = 'ApproximateAgeOfOldestMessage'
    ApproximateNumberOfMessagesDelayed = 'ApproximateNumberOfMessagesDelayed'
    ApproximateNumberOfMessagesNotVisible = 'ApproximateNumberOfMessagesNotVisible'  # noqa: E501
    ApproximateNumberOfMessagesVisible = 'ApproximateNumberOfMessagesVisible'
    NumberOfEmptyReceives = 'NumberOfEmptyReceives'
    NumberOfMessagesDeleted = 'NumberOfMessagesDeleted'
    NumberOfMessagesReceived = 'NumberOfMessagesReceived'
    NumberOfMessagesSent = 'NumberOfMessagesSent'
    SentMessageSize = 'SentMessageSize'


# Resource group name and metric name map
MANDATORY_ALARM_METRICS = {
    ResourceType.LOAD_BALANCER: [CloudwatchMetric.HTTPCode_ELB_5XX_Count],
    ResourceType.TARGET_GROUP: [CloudwatchMetric.HTTPCode_Target_5XX_Count, CloudwatchMetric.TargetResponseTime],  # noqa: E501
    ResourceType.REDIS_CACHE_CLUSTER: [CloudwatchMetric.FreeableMemory, CloudwatchMetric.EngineCPUUtilization, CloudwatchMetric.CPUUtilization, CloudwatchMetric.DatabaseMemoryUsagePercentage, CloudwatchMetric.NewConnections, CloudwatchMetric.NetworkConntrackAllowanceExceeded,CloudwatchMetric.IsMaster], # noqa: E501
    ResourceType.SQS_QUEUE: [CloudwatchMetric.ApproximateNumberOfMessagesVisible],
}


METRIC_RESOURCE_TYPE_MAP = {
    CloudwatchMetric.HTTPCode_ELB_5XX_Count: ResourceType.LOAD_BALANCER,
    CloudwatchMetric.HTTPCode_Target_5XX_Count: ResourceType.TARGET_GROUP,
    CloudwatchMetric.HealthyHostCount: ResourceType.TARGET_GROUP,
    CloudwatchMetric.TargetResponseTime: ResourceType.TARGET_GROUP,
    CloudwatchMetric.FreeableMemory: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.EngineCPUUtilization: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.CPUUtilization: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.DatabaseMemoryUsagePercentage: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.NewConnections: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.NetworkConntrackAllowanceExceeded: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.IsMaster: ResourceType.REDIS_CACHE_CLUSTER,
    CloudwatchMetric.ApproximateAgeOfOldestMessage: ResourceType.SQS_QUEUE,
    CloudwatchMetric.ApproximateNumberOfMessagesDelayed: ResourceType.SQS_QUEUE,  # noqa: E501
    CloudwatchMetric.ApproximateNumberOfMessagesNotVisible: ResourceType.SQS_QUEUE,  # noqa: E501
    CloudwatchMetric.ApproximateNumberOfMessagesVisible: ResourceType.SQS_QUEUE,  # noqa: E501
    CloudwatchMetric.NumberOfEmptyReceives: ResourceType.SQS_QUEUE,
    CloudwatchMetric.NumberOfMessagesDeleted: ResourceType.SQS_QUEUE,
    CloudwatchMetric.NumberOfMessagesReceived: ResourceType.SQS_QUEUE,
    CloudwatchMetric.NumberOfMessagesSent: ResourceType.SQS_QUEUE,
    CloudwatchMetric.SentMessageSize: ResourceType.SQS_QUEUE,
}


class AlarmActionType:
    SNS = 'sns'
    AUTOSCALING = 'autoscaling'


MANDATORY_ACTION_TYPES = [AlarmActionType.SNS]

MONITOR_TAG = 'Monitor'
MONITOR_TAG_INACTIVE_VALUE = 'False'
