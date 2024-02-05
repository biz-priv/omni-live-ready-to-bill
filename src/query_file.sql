with w1 as (
select
    id,
    max(transact_id) as transact_id
from
    orders
group by
    id),
w2 as (
select
    max(transact_id) as transact_id,
    id
from
    stop
group by
    id),
w3 as (
select
    max(transact_id) as transact_id,
    id
from
    movement_order
group by
    id ),
w4 as (
select
    max(transact_id) as transact_id,
    id
from
    movement
group by
    id )

select o.id as order_id,
    s1.actual_departure,
    s1.id as shipper_stop_id,
    s2.id as consignee_stop_id,
    o.status,
    mo.num_of_moves,
    m.brokerage_status,
    date_diff('hour', s1.actual_departure, CURRENT_DATE) as date_diff_hrs,
    o.ready_to_bill
from orders o 
join w1 on o.id = w1.id and o.transact_id = w1.transact_id
left join (select s.* from stop s join w2 on s.id = w2.id and s.transact_id = w2.transact_id) s1 on s1.id = o.shipper_stop_id
left join (select c.* from stop c join w2 on c.id = w2.id and c.transact_id = w2.transact_id) s2 on s2.id = o.consignee_stop_id
left join (select o.id, count(mo1.movement_id) as num_of_moves
    from (select o.id as id from orders o join w1 on o.id = w1.id and o.transact_id = w1.transact_id) o
    left join (select mo.order_id as order_id, mo.movement_id as movement_id from movement_order mo join w3 on mo.id = w3.id and mo.transact_id = w3.transact_id) mo1 on mo1.order_id=o.id
    group by o.id) mo on mo.id = o.id
left join (select * from movement_order mo join w3 on mo.id = w3.id and mo.transact_id = w3.transact_id) mo2 on mo2.order_id = o.id 
left join (select m.* from movement m join w4 on m.id = w4.id and m.transact_id = w4.transact_id) m on m.id = mo2.movement_id
where o.status = 'D'
    and o.ready_to_bill = 'N'
    and mo.num_of_moves = 1
    and m.brokerage_status = 'DELIVERD'
    and date_diff('hour', s1.actual_departure, CURRENT_DATE) >= 96 limit 10;