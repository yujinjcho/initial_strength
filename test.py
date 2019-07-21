import unittest
import main

class Test(unittest.TestCase):

    def test_initial_workout(self):
        workout = main.generate_workout([], {})

        squat = [x for x in workout if x['lift_type'] == 'squat'][0]
        self.assertEqual(squat['sets'][0]['weight'], 45)

        bench = [x for x in workout if x['lift_type'] == 'bench'][0]
        self.assertEqual(bench['sets'][0]['weight'], 45)

        dl = [x for x in workout if x['lift_type'] == 'deadlift'][0]
        self.assertEqual(dl['sets'][0]['weight'], 95)
        self.assertEqual(len(dl['sets']), 1)


    def test_successful_workouts(self):
        previous_workouts = mock_successful_workouts()
        workout = main.generate_workout(previous_workouts, {})

        squat = [x for x in workout if x['lift_type'] == 'squat'][0]
        self.assertEqual(squat['sets'][0]['weight'], 160)

        bench = [x for x in workout if x['lift_type'] == 'bench'][0]
        self.assertEqual(bench['sets'][0]['weight'], 125)

        dl = [x for x in workout if x['lift_type'] == 'deadlift'][0]
        self.assertEqual(dl['sets'][0]['weight'], 180)
        self.assertEqual(len(dl['sets']), 1)

        press_workouts = [x for x in workout if x['lift_type'] == 'press']
        self.assertEqual(len(press_workouts), 0)

    def test_successful_workout_with_settings(self):
        previous_workouts = mock_successful_workouts()
        workout_settings = {
            'increment': {
                'squat': 5,
                'bench': 2.5,
                'press': 2.5,
                'deadlift': 10
            },
            'reps': {
                'squat': 5,
                'bench': 3,
                'press': 3,
            },
            'backoff': {
                'squat': True,
                'bench': True,
                'press': False
            },
            'weights': [
                45,
                25,
                10,
                5,
                2.5
            ]
        }
        workout = main.generate_workout(previous_workouts, workout_settings)

        squat = [x for x in workout if x['lift_type'] == 'squat'][0]
        self.assertEqual(squat['sets'][0]['weight'], 160)
        self.assertEqual(squat['sets'][1]['weight'], 145)
        self.assertEqual(squat['sets'][2]['weight'], 145)
        self.assertEqual(squat['sets'][0]['target_reps'], 5)

        bench = [x for x in workout if x['lift_type'] == 'bench'][0]
        self.assertEqual(bench['sets'][0]['weight'], 122.5)
        self.assertEqual(bench['sets'][0]['target_reps'], 3)

        dl = [x for x in workout if x['lift_type'] == 'deadlift'][0]
        self.assertEqual(dl['sets'][0]['weight'], 185)
        self.assertEqual(dl['sets'][0]['target_reps'], 5)

        press_workouts = [x for x in workout if x['lift_type'] == 'press']
        self.assertEqual(len(press_workouts), 0)

    def test_light_squats(self):
        previous_workouts = mock_successful_workouts()
        workout_settings = {
            'lifts': {
                'light_squat': True
            }
        }
        workout = main.generate_workout(previous_workouts, workout_settings)

        squat = [x for x in workout if x['lift_type'] == 'light_squat'][0]
        # 80% of 160
        self.assertEqual(squat['sets'][0]['weight'], 127.5)
        self.assertEqual(squat['sets'][0]['target_reps'], 5)

        squat_2 = mock_lift('light_squat', 3, 5, 5, 127.5)
        press_2 = mock_lift('bench', 3, 5, 5, 100)
        deadlift_2 = mock_lift('deadlift', 1, 5, 5, 160)
        workout_2 = {
            'workout': [squat_2, press_2, deadlift_2]
        }
        previous_workouts.append(workout_2)
        workout_2 = main.generate_workout(previous_workouts, workout_settings)
        squat = [x for x in workout if x['lift_type'] == 'light_squat'][0]
        # don't do light squats if previously did
        self.assertTrue(not any(x['lift_type'] == 'light_squat' for x in workout_2))

    def test_pulls(self):
        previous_workouts = mock_successful_workouts()
        workout_settings = {
            'lifts': {
                'chinup': True,
                'clean': True
            }
        }
        workout = main.generate_workout(previous_workouts, workout_settings)
        chinup = [x for x in workout if x['lift_type'] == 'chinup']
        self.assertTrue(len(chinup) > 0)

        squat_2 = mock_lift('squat', 3, 5, 5, 160)
        press_2 = mock_lift('bench', 3, 5, 5, 100)
        pull_2 = mock_lift('chinup', 1, 5, 5, 160)
        workout_2 = {
            'workout': [squat_2, press_2, pull_2]
        }
        previous_workouts.append(workout_2)
        next_workout = main.generate_workout(previous_workouts, workout_settings)
        clean = [x for x in next_workout if x['lift_type'] == 'clean']
        self.assertTrue(len(clean) > 0)

        squat_3 = mock_lift('squat', 3, 5, 5, 165)
        press_3 = mock_lift('bench', 3, 5, 5, 100)
        pull_3 = mock_lift('clean', 1, 5, 5, 160)
        workout_3 = {
            'workout': [squat_3, press_3, pull_3]
        }
        previous_workouts.append(workout_3)
        next_next_workout = main.generate_workout(previous_workouts, workout_settings)
        dl = [x for x in next_next_workout if x['lift_type'] == 'deadlift']
        self.assertTrue(len(dl) > 0)


    def test_unsuccessful_squats(self):
        previous_workouts = mock_fail_two()
        workout = main.generate_workout(previous_workouts, {})
        squat = [x for x in workout if x['lift_type'] == 'squat'][0]

        expected = 5 * round((150*.8)/5)
        self.assertEqual(squat['sets'][0]['weight'], expected)

def mock_successful_workouts():
    squat_1 = mock_lift('squat', 3, 5, 5, 145)
    press_1 = mock_lift('press', 3, 5, 5, 100)
    deadlift_1 = mock_lift('deadlift', 1, 5, 5, 160)
    workout_1 = {
        'workout': [squat_1, press_1, deadlift_1]
    }

    squat_2 = mock_lift('squat', 3, 5, 5, 150)
    bench_2 = mock_lift('bench', 3, 5, 5, 120)
    deadlift_2 = mock_lift('deadlift', 1, 5, 5, 165)
    workout_2 = {
        'workout': [squat_2, bench_2, deadlift_2]
    }

    squat_3 = mock_lift('squat', 3, 5, 5, 155)
    press_3 = mock_lift('press', 3, 5, 5, 105)
    deadlift_3 = mock_lift('deadlift', 1, 5, 5, 175)
    workout_3 = {
        'workout': [squat_3, press_3, deadlift_3]
    }

    return [
        workout_1,
        workout_2,
        workout_3
    ]


def mock_fail_one():
    squat_1 = mock_lift('squat', 3, 5, 5, 145)
    press_1 = mock_lift('press', 3, 5, 5, 100)
    deadlift_1 = mock_lift('deadlift', 1, 5, 5, 160)
    workout_1 = {
        'workout': [squat_1, press_1, deadlift_1]
    }

    squat_2 = mock_lift('squat', 3, 4, 5, 150)
    bench_2 = mock_lift('bench', 3, 5, 5, 120)
    deadlift_2 = mock_lift('deadlift', 1, 5, 5, 165)
    workout_2 = {
        'workout': [squat_2, bench_2, deadlift_2]
    }

    return [
        workout_1,
        workout_2
    ]

def mock_fail_two():
    squat = mock_lift('squat', 3, 4, 5, 150)
    press = mock_lift('press', 3, 5, 5, 105)
    deadlift = mock_lift('deadlift', 1, 5, 5, 175)
    workout = {
        'workout': [squat, press, deadlift]
    }
    fail_one = mock_fail_one()
    fail_one.append(workout)
    return fail_one


def mock_lift(lift_type, sets, reps, target_reps, weight):
    return {
         'lift_type': lift_type,
         'sets': [
             {'target_reps':reps, 'weight':weight, 'actual_reps': target_reps}
             for i in range(sets)
         ]
    }


if __name__ == '__main__':
    unittest.main()
