from hypothesis import settings

settings.register_profile("ci", max_examples=1000)
settings.register_profile("dev", max_examples=25)
