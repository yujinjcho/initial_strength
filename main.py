from pprint import pprint

default_weight = 45
default_deadlift_weight = 95

DEADLIFT = 'deadlift'
SQUAT = 'squat'
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
            next_weight = 5 * round((next_weight*.8)/5)
        elif not failed_last:
            next_weight += increment

    # TODO: handle 3x3 and 1RM/2backoff
    number_of_sets = 3 if lift_type != DEADLIFT else 1
    number_of_reps = workout_settings.get('reps', {}).get(lift_type, 5)
    backoff = workout_settings.get('backoff', {}).get(lift_type, False)
    return generate_lift(lift_type, number_of_sets, number_of_reps, next_weight, backoff)


def select_lift_type(lift_type, previous_workouts):
    last_workouts = []

    # select target workouts and reverse order so more recent is first
    for i in range( len(previous_workouts) - 1, -1, -1) :
        workout = previous_workouts[i]
        for lift in workout['workout']:
            if lift['lift_type'] == lift_type:
                last_workouts.append(lift)
            elif lift['lift_type'] in [PRESS, BENCH] and lift_type == 'push':
                last_workouts.append(lift)
            elif lift['lift_type'] in [DEADLIFT, CLEAN, CHINUP] and lift_type == 'pull':
                last_workouts.append(lift)

    return last_workouts


def completed_last_workout(last_workout):
    if last_workout:
        completed = all(
            x['actual_reps'] == x['target_reps']
            for x in last_workout['sets']
        )
    else:
        completed = False

    return completed

def generate_lift(lift_type, sets, reps, weight, backoff):
    if sets == 1:
        weights = [weight]
    elif backoff:
        next_weight = 5 * round((weight*.9)/5)
        # sets will be 3 or 1
        weights = [weight, next_weight, next_weight]
    else:
        weights = [weight]*sets

    sets = [{'target_reps': reps, 'weight': w} for w in weights]
    return {
         'lift_type': lift_type,
         'sets': sets
    }

