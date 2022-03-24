# Dev Log

## Space Savings?

Simply exporting the data as it is may not be ideal.

Here's `du -h` for the data directory, which will be a reasonable baseline:

```
28M   data/sleep              308 users
5.4G  data/heart_rate         354 users
23M   data/blood_oxygenation   81 users
577M  data/stress             359 users
6.0G  data
```

Assuming a very simple linearity, e.g.: (`79`, `80`, `80`, `80`, `80`, `76`)
is the same as (`79`, `80`, `76`) we can potentially remove a huge number of
observations, particularly if long-running measurements like user heart
rate may not change much over the course of an hour.

This shaves off ~3 GB, mostly in the heart rate data.

```
26M   data/sleep
2.1G  data/heart_rate
17M   data/blood_oxygenation
372M  data/stress
2.5G  data
```

For transfer between devices, zipping gets the directory down to
around 363 MB:

```bash
$ du -h data.zip
363M	data.zip
```
