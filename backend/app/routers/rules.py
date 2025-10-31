"""
Rules API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Rule, Library
from app.schemas import RuleCreate, RuleUpdate, RuleResponse
import json

router = APIRouter()


@router.get("", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db)):
    """Get all rules"""
    rules = db.query(Rule).all()
    result = []
    for rule in rules:
        rule_dict = {
            "id": rule.id,
            "library_id": rule.library_id,
            "name": rule.name,
            "enabled": rule.enabled,
            "dry_run": rule.dry_run,
            "logic": rule.logic,
            "conditions": json.loads(rule.conditions_json),
            "immediate_actions": [],
            "delayed_actions": [],
            "created_at": rule.created_at,
            "updated_at": rule.updated_at,
            "library": rule.library
        }
        # Parse actions JSON
        actions = json.loads(rule.actions_json)
        rule_dict["immediate_actions"] = actions.get("immediate", [])
        rule_dict["delayed_actions"] = actions.get("delayed", [])
        result.append(RuleResponse(**rule_dict))
    return result


@router.post("", response_model=RuleResponse)
def create_rule(rule_data: RuleCreate, db: Session = Depends(get_db)):
    """Create a new rule"""
    # Verify library exists
    library = db.query(Library).filter(Library.id == rule_data.library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Debug: Print received conditions
    print(f"Creating rule '{rule_data.name}' with {len(rule_data.conditions)} conditions")
    for i, cond in enumerate(rule_data.conditions):
        print(f"  Condition {i}: field={cond.field}, operator={cond.operator}, value={repr(cond.value)} (type: {type(cond.value).__name__})")
    
    # Store conditions and actions as JSON
    conditions_data = []
    for c in rule_data.conditions:
        cond_dict = c.dict()
        # Ensure value is properly serialized (handle None, empty strings, etc.)
        if cond_dict.get("value") is None and cond_dict.get("operator") in ["IN", "NOT_IN"]:
            print(f"Warning: Condition with {cond_dict['operator']} operator has None value - converting to empty string")
            cond_dict["value"] = ""
        conditions_data.append(cond_dict)
    
    conditions_json = json.dumps(conditions_data)
    actions_json = json.dumps({
        "immediate": [a.dict() for a in rule_data.immediate_actions],
        "delayed": [a.dict() for a in rule_data.delayed_actions]
    })
    
    print(f"Conditions JSON: {conditions_json}")
    
    rule = Rule(
        library_id=rule_data.library_id,
        name=rule_data.name,
        enabled=rule_data.enabled,
        dry_run=rule_data.dry_run,
        logic=rule_data.logic,
        conditions_json=conditions_json,
        actions_json=actions_json
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return RuleResponse(
        id=rule.id,
        library_id=rule.library_id,
        name=rule.name,
        enabled=rule.enabled,
        dry_run=rule.dry_run,
        logic=rule.logic,
        conditions=json.loads(rule.conditions_json),
        immediate_actions=json.loads(rule.actions_json).get("immediate", []),
        delayed_actions=json.loads(rule.actions_json).get("delayed", []),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        library=rule.library
    )


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule_data: RuleUpdate, db: Session = Depends(get_db)):
    """Update a rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    if rule_data.name is not None:
        rule.name = rule_data.name
    if rule_data.enabled is not None:
        rule.enabled = rule_data.enabled
    if rule_data.dry_run is not None:
        rule.dry_run = rule_data.dry_run
    if rule_data.logic is not None:
        rule.logic = rule_data.logic
    if rule_data.conditions is not None:
        rule.conditions_json = json.dumps([c.dict() for c in rule_data.conditions])
    if rule_data.immediate_actions is not None or rule_data.delayed_actions is not None:
        current_actions = json.loads(rule.actions_json)
        if rule_data.immediate_actions is not None:
            current_actions["immediate"] = [a.dict() for a in rule_data.immediate_actions]
        if rule_data.delayed_actions is not None:
            current_actions["delayed"] = [a.dict() for a in rule_data.delayed_actions]
        rule.actions_json = json.dumps(current_actions)
    
    db.commit()
    db.refresh(rule)
    
    return RuleResponse(
        id=rule.id,
        library_id=rule.library_id,
        name=rule.name,
        enabled=rule.enabled,
        dry_run=rule.dry_run,
        logic=rule.logic,
        conditions=json.loads(rule.conditions_json),
        immediate_actions=json.loads(rule.actions_json).get("immediate", []),
        delayed_actions=json.loads(rule.actions_json).get("delayed", []),
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        library=rule.library
    )


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}

