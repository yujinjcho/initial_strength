from pprint import pprint

default_weight = 45
default_deadlift_weight = 95

DEFAULT_SETS = 3
DEADLIFT_SETS = 1

DELOAD_PERCENT = .8
BACKOFF_PERCENT = .9

DEADLIFT = 'deadlift'
SQUAT = 'squat'
LIGHT_SQUAT = 'light_squat'
BOTH_SQUAT = 'both_squat'
PRESS = 'press'
BENCH = 'bench'
CHINUP = 'chinup'
CLEAN = 'clean'

def generate_workout(previous_workouts, workout_settings):

    # SQUATS
    # ignore light squats for now
    # just need to check if last squat was successful
    next_squat = generate_next_lift(previous_workouts, SQUAT, workout_settings)

    # PUSH
    recent_push_workout = select_lift_type('push', previous_workouts)
    next_push_lift_type = BENCH if (not recent_push_workout or recent_push_workout[0]['lift_type'] == PRESS) else PRESS

    next_push = generate_next_lift(previous_workouts, next_push_lift_type, workout_settings)

    # DEADLIFT only
    next_pull = generate_next_lift(previous_workouts, DEADLIFT, workout_settings)

    return [
        next_squat,
        next_push,
        next_pull
    ]

def generate_next_lift(previous_workouts, lift_type, workout_settings):
    # get previous workouts
    previous_lifts_for_type = select_lift_type(lift_type, previous_workouts)
    failed_lift = lambda l: any(s['target_reps'] != s['actual_reps'] for s in l['sets'])

    increment = workout_settings.get('increment', {}).get(lift_type, 5)
    min_weight_unit = min(workout_settings.get('weight', [2.5]))

    # if no previous workout:
    if not previous_lifts_for_type:
        next_weight = default_deadlift_weight if (lift_type == DEADLIFT) else default_weight

    # there is only one workout
    elif len(previous_lifts_for_type) == 1:

        next_weight = previous_lifts_for_type[0]['sets'][0]['weight']
        if not failed_lift(previous_lifts_for_type[0]):
            next_weight += increment

    # there is at least two workouts
    else:
        next_weight = previous_lifts_for_type[0]['sets'][0]['weight']

        failed_last = failed_lift(previous_lifts_for_type[0])
        failed_prior = failed_lift(previous_lifts_for_type[1])

        if failed_last and failed_prior:
            next_weight = min_weight_unit * round((next_weight * DELOAD_PERCENT)/min_weight_unit)
        elif not failed_last:
            next_weight += increment

    # handle light squats since special case
    if should_do_light_squat(previous_workouts, lift_type, workout_settings):
        lift_type = LIGHT_SQUAT
        next_weight = min_weight_unit * round((next_weight * DELOAD_PERCENT)/min_weight_unit)

    lift_config = {
        'lift_type': lift_type,
        'weight': next_weight,
        'number_of_sets': DEFAULT_SETS if lift_type != DEADLIFT else DEADLIFT_SETS,
        'number_of_reps': workout_settings.get('reps', {}).get(lift_type, 5),
        'is_backoff': workout_settings.get('backoff', {}).get(lift_type, False),
        'min_weight_unit': min_weight_unit
    }
    return generate_lift(lift_config)


def select_lift_type(lift_type, previous_workouts):
    last_workouts = []

    # select target workouts and reverse order so more recent is first
    for i in range( len(previous_workouts) - 1, -1, -1) :
        workout = previous_workouts[i]
        for lift in workout['workout']:
            if lift['lift_type'] == lift_type:
                last_workouts.append(lift)
            elif lift['lift_type'] in [SQUAT, LIGHT_SQUAT] and lift_type == BOTH_SQUAT:
                last_workouts.append(lift)
            elif lift['lift_type'] in [PRESS, BENCH] and lift_type == 'push':
                last_workouts.append(lift)
            elif lift['lift_type'] in [DEADLIFT, CLEAN, CHINUP] and lift_type == 'pull':
                last_workouts.append(lift)

    return last_workouts

def should_do_light_squat(previous_workouts, lift_type, workout_settings):
    if not lift_type == SQUAT:
        return False

    if not workout_settings.get('lifts', {}).get(LIGHT_SQUAT, False):
        return False

    squat_workouts = select_lift_type(BOTH_SQUAT, previous_workouts)
    if len(squat_workouts) < 2:
        return False

    if any([x['lift_type'] == LIGHT_SQUAT for x in squat_workouts[:2]]):
        return False

    return True

def completed_last_workout(last_workout):
    if last_workout:
        completed = all(
            x['actual_reps'] == x['target_reps']
            for x in last_workout['sets']
        )
    else:
        completed = False

    return completed

def generate_lift(lift_config):
    weight = lift_config['weight']

    if lift_config['number_of_sets'] == 1:
        weights = [weight]
    elif lift_config['is_backoff']:
        next_weight = 5 * round((weight * BACKOFF_PERCENT)/5)
        # sets will be 3 or 1
        weights = [weight, next_weight, next_weight]
    else:
        weights = [weight] * lift_config['number_of_sets']

    sets = [{'target_reps': lift_config['number_of_reps'], 'weight': w} for w in weights]
    return {
         'lift_type': lift_config['lift_type'],
         'sets': sets
    }

