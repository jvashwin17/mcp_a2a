-- Seed Customers
INSERT INTO customers (id, name, email) VALUES
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Alice Smith', 'alice@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'Bob Johnson', 'bob@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'Charlie Brown', 'charlie@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Diana Prince', 'diana@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Evan Davis', 'evan@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'Fiona Gallagher', 'fiona@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a17', 'George Costanza', 'george@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 'Hannah Montana', 'hannah@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a19', 'Ian Malcolm', 'ian@example.com'),
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'Julia Roberts', 'julia@example.com');

-- Seed Orders
INSERT INTO orders (id, customer_id, total_amount, order_status) VALUES
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 150.50, 'completed'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 200.00, 'In Progress'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 45.99, 'Received'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 1200.00, 'started'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b15', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 34.50, 'canceled'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b16', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 89.99, 'on hold'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b17', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 500.25, 'completed'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b18', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 15.00, 'In Progress'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b19', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a19', 249.99, 'Received'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b20', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 1050.00, 'completed'),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380b21', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 60.00, 'started');

-- Seed Support Tickets
INSERT INTO support_tickets (id, customer_id, issue, status) VALUES
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Login issue on mobile app', 'Open'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'Forgot password', 'Resolved'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c13', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'Order not received', 'In Progress'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'Payment declined incorrectly', 'Open'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c15', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15', 'Feature request: dark mode', 'Closed'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c16', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16', 'App crashes on start', 'Escalated'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c17', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a17', 'Billing details update', 'Resolved'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c18', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a18', 'Incorrect item sent', 'In Progress'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c19', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a19', 'Account data export request', 'Open'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c20', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a20', 'Subscription cancellation', 'Resolved'),
('c0eebc99-9c0b-4ef8-bb6d-6bb9bd380c21', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Follow-up on previous login issue', 'Open');
