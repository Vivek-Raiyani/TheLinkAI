def with_retry(state, fn, counter_field: str, MAX_RETRIES=2):
    try:
        return fn(state)
    except Exception as e:
        retries = getattr(state, counter_field)
        if retries >= MAX_RETRIES:
            state.status = "failed"
            state.error = str(e)
            return state

        setattr(state, counter_field, retries + 1)
        return state
