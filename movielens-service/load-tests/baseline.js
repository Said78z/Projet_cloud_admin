/**
 * k6 baseline load test for the MovieLens service.
 *
 * Run:
 *   k6 run load-tests/baseline.js
 *
 * Override the base URL:
 *   k6 run -e BASE_URL=http://localhost:8000 load-tests/baseline.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const errorRate = new Rate("errors");

export const options = {
  stages: [
    { duration: "30s", target: 10 },  // ramp-up to 10 VUs
    { duration: "1m",  target: 10 },  // hold at 10 VUs
    { duration: "30s", target: 50 },  // ramp-up to 50 VUs
    { duration: "1m",  target: 50 },  // hold at 50 VUs
    { duration: "30s", target: 0  },  // ramp-down
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],  // 95th percentile < 500 ms
    errors:            ["rate<0.01"],  // error rate < 1 %
  },
};

export default function () {
  const params = { tags: { name: "health" } };

  // Health check
  let res = http.get(`${BASE_URL}/health`, params);
  errorRate.add(!check(res, { "health status 200": (r) => r.status === 200 }));

  sleep(0.5);

  // Search movies by title
  res = http.get(`${BASE_URL}/movies?title=star&page=1&page_size=10`, {
    tags: { name: "search_title" },
  });
  errorRate.add(!check(res, { "search status 200": (r) => r.status === 200 }));

  sleep(0.5);

  // Filter movies by genre
  res = http.get(`${BASE_URL}/movies?genre=Action&page=1&page_size=10`, {
    tags: { name: "search_genre" },
  });
  errorRate.add(!check(res, { "genre filter status 200": (r) => r.status === 200 }));

  sleep(0.5);

  // Top-rated movies
  res = http.get(`${BASE_URL}/movies/top-rated?limit=10&min_ratings=50`, {
    tags: { name: "top_rated" },
  });
  errorRate.add(!check(res, { "top-rated status 200": (r) => r.status === 200 }));

  sleep(0.5);

  // Genre stats
  res = http.get(`${BASE_URL}/stats/genres`, { tags: { name: "genre_stats" } });
  errorRate.add(!check(res, { "genre stats status 200": (r) => r.status === 200 }));

  sleep(1);
}
