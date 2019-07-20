import unittest
import main

class Test(unittest.TestCase):

    def test_initial_workout(self):
        workout = main.generate_workout([], None)

        squat = [x for x in reversed(workout) if x['lift_type'] == 'squat'][0]
        self.assertEqual(squat['sets'][0]['weight'], 45)

        bench = [x for x in reversed(workout) if x['lift_type'] == 'bench'][0]
        self.assertEqual(bench['sets'][0]['weight'], 45)

        dl = [x for x in reversed(workout) if x['lift_type'] == 'deadlift'][0]
        self.assertEqual(dl['sets'][0]['weight'], 95)
        self.assertEqual(len(dl['sets']), 1)


    def test_successful_workouts(self):
        previous_workouts = mock_successful_workouts()
        workout = main.generate_workout(previous_workouts, None)

        squat = [x for x in reversed(workout) if x['lift_type'] == 'squat'][0]
        self.assertEqual(squat['sets'][0]['weight'], 160)

        bench = [x for x in reversed(workout) if x['lift_type'] == 'bench'][0]
        self.assertEqual(bench['sets'][0]['weight'], 125)

        dl = [x for x in reversed(workout) if x['lift_type'] == 'deadlift'][0]
        self.assertEqual(dl['sets'][0]['weight'], 180)
        self.assertEqual(len(dl['sets']), 1)

        press_workouts = [x for x in reversed(workout) if x['lift_type'] == 'press']
        self.assertEqual(len(press_workouts), 0)

    def test_unsuccessful_squats(self):
        previous_workouts = mock_unsuccessful_workouts()
        workout = main.generate_workout(previous_workouts, None)
        squat = [x for x in reversed(workout) if x['lift_type'] == 'squat'][0]

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

def mock_unsuccessful_workouts():
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

    squat_3 = mock_lift('squat', 3, 4, 5, 150)
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
