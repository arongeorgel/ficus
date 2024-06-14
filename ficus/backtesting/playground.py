def cause_runtime_error():
    my_dict = {'a': 1, 'b': 2, 'c': 3}

    # This will raise a RuntimeError
    try:
        for key in my_dict:
            print(f"Processing key: {key}")
            # Modify the dictionary during iteration
            my_dict[key + '_new'] = my_dict.pop(key)
    except RuntimeError as e:
        print(f"Caught an exception: {e}")

if __name__ == "__main__":
    cause_runtime_error()
