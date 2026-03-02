"""Grouping observations by category and by unit/room."""

from services.lead_paint.schemas import ObservationSchema


def group_observations_by_category(
    observations: list[ObservationSchema],
) -> tuple[list[ObservationSchema], list[ObservationSchema], list[ObservationSchema]]:
    """Split observations into three lists by category.

    - hazards: category == 'HAZARD'
    - future_risk: category == 'FUTURE_RISK'
    - excluded_components: category == 'EXCLUSION'

    Args:
        observations: Flat list of observations from any parser or combined result.

    Returns:
        Tuple of (hazards_list, future_risk_list, excluded_components_list).

    """
    hazards: list[ObservationSchema] = []
    future_risk: list[ObservationSchema] = []
    excluded_components: list[ObservationSchema] = []

    for obs in observations:
        if obs.category == 'HAZARD':
            hazards.append(obs)
        elif obs.category == 'FUTURE_RISK':
            future_risk.append(obs)
        elif obs.category == 'EXCLUSION':
            excluded_components.append(obs)

    return (hazards, future_risk, excluded_components)


def group_by_unit_and_room(
    observations: list[ObservationSchema],
    *,
    use_side_as_room: bool = False,
) -> tuple[
    dict[str, dict[str, list[ObservationSchema]]],
    dict[str, list[ObservationSchema]],
]:
    """Group observations by unit and room.

    - by_unit: unit_id -> { room_name -> [observations] }. Only for obs with unit set.
    - by_room: room_name -> [observations]. For obs with unit=null (or when use_side_as_room
      and room is null, uses side as room key e.g. "Side A").

    Args:
        observations: List of observations (e.g. hazards or future_risk).
        use_side_as_room: If True, for items with no room use side as group key (e.g. "Side A").
                          Use for exterior where unit/room are null and side is the grouping.

    Returns:
        Tuple (by_unit_dict, by_room_dict). Keys are strings (unit id, room name).
    """
    by_unit: dict[str, dict[str, list[ObservationSchema]]] = {}
    by_room: dict[str, list[ObservationSchema]] = {}

    for obs in observations:
        unit_id = (obs.unit or '').strip() or None
        room_name = (obs.room or '').strip() or None
        if use_side_as_room and not room_name and obs.side:
            room_name = f'Side {obs.side}'
        if not room_name:
            room_name = 'Unspecified'

        if unit_id:
            if unit_id not in by_unit:
                by_unit[unit_id] = {}
            if room_name not in by_unit[unit_id]:
                by_unit[unit_id][room_name] = []
            by_unit[unit_id][room_name].append(obs)
        else:
            if room_name not in by_room:
                by_room[room_name] = []
            by_room[room_name].append(obs)

    return (by_unit, by_room)
