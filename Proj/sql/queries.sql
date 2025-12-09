PRAGMA foreign_keys = ON;

SELECT id, name, phone, org, email, password_hash, created_at
FROM visitor
WHERE email = :email
LIMIT 1;

SELECT id, name, phone, org, email, password_hash, created_at
FROM visitor
WHERE phone = :phone
LIMIT 1;

SELECT id, name, phone, org, email, password_hash, created_at
FROM visitor
WHERE email = :login OR phone = :login
LIMIT 1;


SELECT id, name, phone, org, email, created_at
FROM visitor
WHERE id = :me;

UPDATE visitor
SET name = :name,
    phone = :phone,
    org = :org,
    email = :email
WHERE id = :me;

UPDATE visitor
SET password_hash = :password_hash
WHERE id = :me;


SELECT id, campus, name
FROM location
WHERE is_active = 1
  AND campus = :campus
ORDER BY name ASC;

SELECT id, campus, name, is_active
FROM location
WHERE id = :location_id;


INSERT INTO reservation (
  visitor_id, start_time, end_time,
  location, location_id, purpose,
  status, is_driving, plate_number
) VALUES (
  :visitor_id, :start_time, :end_time,
  :location_name, :location_id, :purpose,
  'pending', :is_driving, :plate_number
);

SELECT *
FROM reservation
WHERE visitor_id = :me
  AND (:status IS NULL OR status = :status)
ORDER BY start_time DESC;

UPDATE reservation
SET start_time   = :start_time,
    end_time     = :end_time,
    location     = :location_name,
    location_id  = :location_id,
    purpose      = :purpose,
    is_driving   = :is_driving,
    plate_number = :plate_number,
    updated_at   = CURRENT_TIMESTAMP
WHERE id = :id
  AND visitor_id = :me
  AND status = 'pending';

DELETE FROM reservation
WHERE id = :id
  AND visitor_id = :me
  AND status = 'pending';

SELECT r.id,
       v.name  AS visitor_name,
       v.org   AS visitor_org,
       r.start_time, r.end_time,
       l.campus,
       l.name  AS location,
       r.purpose, r.status,
       r.is_driving, r.plate_number
FROM reservation r
JOIN visitor  v ON v.id = r.visitor_id
LEFT JOIN location l ON l.id = r.location_id
WHERE (:location_id IS NULL OR r.location_id = :location_id)
  AND (:date IS NULL OR DATE(r.start_time) = :date)
ORDER BY r.start_time DESC;

SELECT r.*
FROM reservation r
WHERE r.visitor_id = :visitor_id
ORDER BY r.start_time DESC;


UPDATE reservation
SET status = :decision,          
    updated_at = CURRENT_TIMESTAMP
WHERE id = :reservation_id
  AND status = 'pending';

INSERT INTO notification (visitor_id, type, reservation_id, title, body, is_read)
VALUES (:visitor_id, 'reservation_status', :reservation_id,
        'Reservation Approval Result', :body_text, 0);


WITH day AS (
  SELECT :d AS d_start, DATE(:d, '+1 day') AS d_end
)
SELECT r.location_id,
       l.name AS location_name,
       COUNT(r.id) AS reservation_count,
       SUM(CASE WHEN r.status='approved' THEN 1 ELSE 0 END) AS approved_count
FROM reservation r
JOIN location l ON l.id = r.location_id
JOIN day      d ON 1=1
WHERE r.start_time >= d.d_start AND r.start_time < d.d_end
GROUP BY r.location_id, l.name
ORDER BY reservation_count DESC, approved_count DESC
LIMIT 1;

WITH day AS (
  SELECT :d AS d_start, DATE(:d, '+1 day') AS d_end
)
SELECT r.location_id,
       l.name AS location_name,
       SUM(CASE WHEN r.status='approved' THEN 1 ELSE 0 END) AS approved_count,
       COUNT(r.id) AS reservation_count
FROM reservation r
JOIN location l ON l.id = r.location_id
JOIN day      d ON 1=1
WHERE r.start_time >= d.d_start AND r.start_time < d.d_end
GROUP BY r.location_id, l.name
ORDER BY approved_count DESC, reservation_count DESC
LIMIT 1;

WITH day AS (
  SELECT :d AS d_start, DATE(:d, '+1 day') AS d_end
)
SELECT
  COUNT(*) AS total_reservations,
  SUM(CASE WHEN status='pending'  THEN 1 ELSE 0 END) AS pending_count,
  SUM(CASE WHEN status='approved' THEN 1 ELSE 0 END) AS approved_count,
  SUM(CASE WHEN status='denied'   THEN 1 ELSE 0 END) AS denied_count
FROM reservation r
JOIN day d ON 1=1
WHERE r.start_time >= d.d_start AND r.start_time < d.d_end;

WITH day AS (
  SELECT :d AS d_start, DATE(:d, '+1 day') AS d_end
),
uv_days AS (
  SELECT DISTINCT r.visitor_id, DATE(r.start_time) AS d
  FROM reservation r
  JOIN day d ON r.start_time < d.d_end
  WHERE r.status='approved'
)
SELECT COUNT(*) AS total_unique_visitor_days_up_to_date
FROM uv_days;

SELECT *
FROM notification
WHERE visitor_id = :me
  AND (:unread_only = 0 OR is_read = 0)
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;

SELECT COUNT(*) AS unread
FROM notification
WHERE visitor_id = :me
  AND is_read = 0;

UPDATE notification
SET is_read = :is_read     
WHERE id = :notification_id
  AND visitor_id = :me;

UPDATE notification
SET is_read = 1
WHERE visitor_id = :me
  AND is_read = 0;


SELECT COUNT(*) AS overlap_count
FROM reservation
WHERE location_id = :location_id
  AND DATE(start_time) = DATE(:s)
  AND status IN ('pending','approved')   
  AND NOT (end_time <= :s OR start_time >= :e);

SELECT COUNT(*) AS my_count_today
FROM reservation
WHERE visitor_id = :me
  AND DATE(start_time) = :d;

SELECT CASE
  WHEN :plate IS NULL THEN 1
  WHEN :plate GLOB '[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]' THEN 1
  ELSE 0
END AS plate_ok;

SELECT CASE
  WHEN DATE(:s) = DATE(:e)
   AND time(:s) >= '09:00'
   AND time(:e) <= '17:00'
  THEN 1 ELSE 0
END AS time_window_ok;



