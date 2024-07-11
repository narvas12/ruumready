from rest_framework import serializers

def checkBool(value):
    instance = isinstance(value, bool)
        
    if not instance:
        raise serializers.ValidationError('Value has to be either true of false')