# Gym Log

## Screenshots

| Home                                                         | Workout                                                      | Exercise                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------- |
| ![Screenshot of homepage](.screenshots/Home.png)             | ![Screenshot of workout page](.screenshots/Workout.png)      | ![Screenshot of exercise page](.screenshots/Exercise.png) |
| Edit workout                                                 | Edit set                                                     |                                                           |
| ![Screenshot of edit workout page](.screenshots/EditWorkout.png) | ![Screen shot of edit set dialog on exercise page](.screenshots/EditSet.png) |                                                           |



## Deployment

Build the docker container

```bash
docker buildx build -t gymlog:latest .
```

Then modify the template docker-compose.yml file to set the correct path for the `data` directory and run with

```bash
docker-compose up -d
```