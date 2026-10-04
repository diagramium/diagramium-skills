#!/usr/bin/env python3
"""Writes skills/diagramium-diagrams/examples/<mode>.json — one realistic,
valid document per diagram type. Every file is checked by
scripts/validate.py and, before a release, opened in the real app
(see CONTRIBUTING.md). Run from the repo root: python3 tools/make_examples.py
"""
import json, pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "skills" / "diagramium-diagrams" / "examples"
OUT.mkdir(parents=True, exist_ok=True)


def doc(mode, state):
    return {"app": "flow-diagram", "version": 2, "mode": mode, "state": state}


def g(node, gc, gr):
    """Grid cell plus the fallback x/y an older engine renders."""
    node.update({"gc": gc, "gr": gr, "x": 120 + gc * 260, "y": 110 + gr * 160})
    return node


def grid(title, theme, nodes, edges, **extra):
    st = {"format": 2, "layout": "grid", "title": title, "theme": theme,
          "nodes": nodes, "edges": edges}
    st.update(extra)
    return st


EX = {}

# ---------------------------------------------------------------- sequence
EX["sequence"] = doc("sequence", {
    "title": "Signing in with a password", "theme": "quartz",
    "actors": [
        {"id": "user", "kind": "actor", "name": "User"},
        {"id": "app", "name": "Web app"},
        {"id": "api", "kind": "control", "name": "Auth API"},
        {"id": "db", "kind": "database", "name": "Users DB"}],
    "items": [
        {"id": "m1", "type": "message", "from": "user", "to": "app", "text": "Enter email and password", "style": "sync"},
        {"id": "m2", "type": "message", "from": "app", "to": "api", "text": "POST /login", "style": "sync"},
        {"id": "m3", "type": "message", "from": "api", "to": "db", "text": "Find user by email", "style": "sync"},
        {"id": "m4", "type": "message", "from": "db", "to": "api", "text": "Password hash", "style": "reply"},
        {"id": "f1", "type": "fragStart", "kind": "alt", "label": "password matches"},
        {"id": "m5", "type": "message", "from": "api", "to": "app", "text": "Session token", "style": "reply"},
        {"id": "f2", "type": "fragElse", "label": "wrong password"},
        {"id": "m6", "type": "message", "from": "api", "to": "app", "text": "401 Unauthorized", "style": "reply"},
        {"id": "f3", "type": "fragEnd"},
        {"id": "n1", "type": "note", "pos": "over", "actor": "user", "actor2": "app", "text": "Everything travels over HTTPS"}],
    "narration": {
        "1": "The user types their email and password into the sign-in form.",
        "2": "The web app sends those credentials to the authentication API.",
        "3": "The API looks the user up by email address.",
        "4": "The database returns the stored password hash, never the password itself.",
        "5": "Now there are two possible outcomes.",
        "6": "If the hash matches, the API issues a session token.",
        "7": "Otherwise…",
        "8": "…it refuses with a 401, and says nothing about which part was wrong.",
        "9": "That is the whole exchange.",
        "10": "And every one of these messages travels encrypted.",
        "__why3": "Looking up by email first means the password is only ever compared, never searched for."}})

# ---------------------------------------------------------------- flowchart
EX["flowchart"] = doc("flowchart", grid("Password reset", "doodle", [
    g({"id": "n1", "type": "start", "text": "Request a reset"}, 0, 0),
    g({"id": "n2", "type": "process", "text": "Email a reset link"}, 0, 1),
    g({"id": "n3", "type": "decision", "text": "Link still valid?"}, 0, 2),
    g({"id": "n4", "type": "process", "text": "Choose a new password"}, 0, 3),
    g({"id": "n5", "type": "end", "text": "Signed in"}, 0, 4),
    g({"id": "n6", "type": "process", "text": "Show 'link expired'"}, 1, 2)],
    [{"id": "e1", "from": "n1", "to": "n2"},
     {"id": "e2", "from": "n2", "to": "n3"},
     {"id": "e3", "from": "n3", "to": "n4", "label": "yes"},
     {"id": "e4", "from": "n4", "to": "n5"},
     {"id": "e5", "from": "n3", "to": "n6", "label": "no", "style": "dashed"},
     {"id": "e6", "from": "n6", "to": "n2", "label": "send a new link", "style": "dashed"}]))

# ---------------------------------------------------------------- statemachine
EX["statemachine"] = doc("statemachine", grid("Order lifecycle", "obsidian", [
    g({"id": "s0", "type": "initial", "text": ""}, 0, 1),
    g({"id": "s1", "type": "simple", "text": "Pending", "entry": "reserve stock"}, 1, 1),
    g({"id": "s2", "type": "simple", "text": "Paid"}, 2, 1),
    g({"id": "s3", "type": "simple", "text": "Shipped"}, 3, 1),
    g({"id": "s4", "type": "simple", "text": "Cancelled", "entry": "release stock"}, 2, 2),
    g({"id": "s5", "type": "final", "text": ""}, 4, 1)],
    [{"id": "t1", "from": "s0", "to": "s1"},
     {"id": "t2", "from": "s1", "to": "s2", "label": "payment ok"},
     {"id": "t3", "from": "s2", "to": "s3", "label": "dispatched"},
     {"id": "t4", "from": "s1", "to": "s4", "label": "timeout / cancel"},
     {"id": "t5", "from": "s3", "to": "s5", "label": "delivered"}]))

# ---------------------------------------------------------------- swimlane
EX["swimlane"] = doc("swimlane", {
    "format": 2, "layout": "grid", "title": "Expense approval", "theme": "metro",
    "lanes": [{"id": "L1", "name": "Employee", "height": 160},
              {"id": "L2", "name": "Manager", "height": 160},
              {"id": "L3", "name": "Finance", "height": 160}],
    "phases": [{"id": "P1", "label": "Submit", "width": 260},
               {"id": "P2", "label": "Review", "width": 260},
               {"id": "P3", "label": "Pay", "width": 260}],
    "nodes": [
        {"id": "a", "type": "start", "text": "Submit receipt", "laneId": "L1", "yInLane": 80, "gc": 0, "x": 120},
        {"id": "b", "type": "decision", "text": "Within policy?", "laneId": "L2", "yInLane": 80, "gc": 1, "x": 360},
        {"id": "c", "type": "process", "text": "Reimburse", "laneId": "L3", "yInLane": 80, "gc": 2, "x": 600},
        {"id": "d", "type": "end", "text": "Paid", "laneId": "L1", "yInLane": 80, "gc": 2, "x": 600},
        {"id": "r", "type": "process", "text": "Ask for details", "laneId": "L1", "yInLane": 80, "gc": 1, "x": 360}],
    "edges": [{"id": "e1", "from": "a", "to": "b"},
              {"id": "e2", "from": "b", "to": "c", "label": "yes"},
              {"id": "e3", "from": "c", "to": "d"},
              {"id": "e4", "from": "b", "to": "r", "label": "no", "style": "dashed"}],
    "narration": {
        "1": "An employee submits a receipt.",
        "2": "Their manager checks it against the expense policy.",
        "3": "If it passes, finance reimburses it.",
        "4": "And the money lands back with the employee.",
        "5": "If it does not, the employee is asked for more detail."}})

# ---------------------------------------------------------------- kanban
EX["kanban"] = doc("kanban", {
    "title": "Sprint 12", "theme": "stickynote",
    "lanes": [{"id": "todo", "name": "To do", "height": 260},
              {"id": "doing", "name": "In progress", "height": 260},
              {"id": "review", "name": "Review", "height": 260},
              {"id": "done", "name": "Done", "height": 260}],
    "nodes": [
        {"id": "k1", "type": "process", "text": "Sign-in page", "laneId": "todo", "yInLane": 50, "x": 0},
        {"id": "k2", "type": "process", "text": "Password reset", "laneId": "todo", "yInLane": 130, "x": 0},
        {"id": "k3", "type": "process", "text": "Session API", "laneId": "doing", "yInLane": 50, "x": 0, "animFx": "pulse"},
        {"id": "k4", "type": "process", "text": "Rate limiting", "laneId": "review", "yInLane": 50, "x": 0},
        {"id": "k5", "type": "process", "text": "Project setup", "laneId": "done", "yInLane": 50, "x": 0},
        {"id": "k6", "type": "process", "text": "CI pipeline", "laneId": "done", "yInLane": 130, "x": 0}],
    "edges": []})

# ---------------------------------------------------------------- orgchart
EX["orgchart"] = doc("orgchart", {
    "title": "Product organisation", "theme": "executive",
    "people": [
        {"id": "ceo", "name": "Ana Ruiz", "title": "Chief Executive"},
        {"id": "cpo", "name": "Ben Okafor", "title": "Chief Product Officer", "parent": "ceo", "dept": "Product"},
        {"id": "cto", "name": "Chen Wei", "title": "Chief Technology Officer", "parent": "ceo", "dept": "Engineering"},
        {"id": "des", "name": "Design", "kind": "department", "parent": "cpo"},
        {"id": "pm", "name": "Dana Kim", "title": "Group PM", "parent": "cpo"},
        {"id": "plat", "name": "Platform", "kind": "department", "parent": "cto"},
        {"id": "sre", "name": "Open role", "title": "Staff SRE", "kind": "vacant", "parent": "cto"}],
    "narration": {
        "1": "Ana leads the company.",
        "2": "Ben owns what we build.",
        "3": "Chen owns how we build it.",
        "4": "Design sits inside product.",
        "5": "Dana coordinates the product managers.",
        "6": "The platform team keeps everything running.",
        "7": "And we are hiring a staff site-reliability engineer."}})

# ---------------------------------------------------------------- sitemap
EX["sitemap"] = doc("sitemap", {
    "title": "Marketing site", "theme": "bento",
    "people": [
        {"id": "home", "name": "Home"},
        {"id": "prod", "name": "Product", "kind": "department", "parent": "home"},
        {"id": "feat", "name": "Features", "parent": "prod"},
        {"id": "price", "name": "Pricing", "parent": "prod"},
        {"id": "res", "name": "Resources", "kind": "department", "parent": "home"},
        {"id": "blog", "name": "Blog", "parent": "res"},
        {"id": "docs", "name": "Docs", "kind": "contractor", "parent": "res", "title": "docs.example.com"},
        {"id": "careers", "name": "Careers", "kind": "vacant", "parent": "home", "title": "coming soon"}]})

# ---------------------------------------------------------------- mindmap
EX["mindmap"] = doc("mindmap", {
    "title": "Launch plan", "theme": "canvas", "rootId": "r",
    "nodes": [
        {"id": "r", "text": "Product launch", "shape": "ellipse"},
        {"id": "m", "text": "Marketing", "parent": "r", "side": "left", "color": "#6d7cff"},
        {"id": "m1", "text": "Launch blog post", "parent": "m"},
        {"id": "m2", "text": "Newsletter", "parent": "m"},
        {"id": "e", "text": "Engineering", "parent": "r", "side": "right", "color": "#10b981"},
        {"id": "e1", "text": "Feature flags", "parent": "e"},
        {"id": "e2", "text": "Load testing", "parent": "e"},
        {"id": "s", "text": "Support", "parent": "r", "side": "right", "color": "#f59e0b"},
        {"id": "s1", "text": "Help-centre articles", "parent": "s"}],
    "links": [{"id": "l1", "from": "m1", "to": "e1", "label": "announce what ships", "style": "dashed"}]})

# ---------------------------------------------------------------- timeline
EX["timeline"] = doc("timeline", {
    "title": "From idea to version 1", "theme": "editorial", "track": "chevron",
    "showGaps": True, "layout": "straight",
    "events": [
        {"id": "e1", "date": "2025-01", "title": "Idea", "desc": "A weekend prototype", "emoji": "💡"},
        {"id": "e2", "date": "2025-04", "title": "First users", "kind": "milestone"},
        {"id": "e3", "date": "Q3 2025", "title": "Public beta", "kind": "release"},
        {"id": "e4", "date": "2026-01-15", "title": "Version 1.0", "kind": "release", "desc": "General availability"},
        {"id": "e5", "date": "2026-06-30", "title": "Security audit", "kind": "deadline"}],
    "eras": [{"id": "p1", "label": "Build", "from": "e1", "to": "e2"},
             {"id": "p2", "label": "Grow", "from": "e3", "to": "e5"}]})

# ---------------------------------------------------------------- gantt
EX["gantt"] = doc("gantt", {
    "title": "Q1 website relaunch", "theme": "quartz", "ganttStyle": "premium",
    "startDate": "2026-01-05", "showCritical": True,
    "tasks": [
        {"id": "t1", "name": "Discovery", "start": 0, "days": 5, "done": 100},
        {"id": "t2", "name": "Design", "start": 5, "days": 10, "done": 60},
        {"id": "t3", "name": "Content", "start": 5, "days": 15, "done": 20},
        {"id": "t4", "name": "Build", "start": 15, "days": 12},
        {"id": "t5", "name": "QA", "start": 27, "days": 4},
        {"id": "m1", "name": "Launch", "start": 31, "days": 0}],
    "deps": [{"from": "t1", "to": "t2"}, {"from": "t1", "to": "t3"},
             {"from": "t2", "to": "t4"}, {"from": "t4", "to": "t5"},
             {"from": "t3", "to": "t5"}, {"from": "t5", "to": "m1"}]})

# ---------------------------------------------------------------- venn
EX["venn"] = doc("venn", {
    "title": "What a product designer knows", "theme": "glassmorphism",
    "sets": [
        {"id": "s1", "label": "Design", "cx": 470, "cy": 248, "r": 150},
        {"id": "s2", "label": "Engineering", "cx": 550, "cy": 386, "r": 150},
        {"id": "s3", "label": "Business", "cx": 390, "cy": 386, "r": 150}],
    "items": [
        {"id": "i1", "text": "Visual craft", "x": 470, "y": 180},
        {"id": "i2", "text": "APIs", "x": 610, "y": 430},
        {"id": "i3", "text": "Pricing", "x": 330, "y": 430},
        {"id": "i4", "text": "Product sense", "x": 470, "y": 340}]})

# ---------------------------------------------------------------- journeymap
EX["journeymap"] = doc("journeymap", {
    "title": "New-customer onboarding", "theme": "forest", "stageWidth": 200,
    "stages": [{"id": "st1", "name": "Sign up"}, {"id": "st2", "name": "Set up"},
               {"id": "st3", "name": "First win"}, {"id": "st4", "name": "Habit"}],
    "rows": [{"id": "r1", "name": "Doing", "kind": "text"},
             {"id": "r2", "name": "Feeling", "kind": "emotion"},
             {"id": "r3", "name": "Satisfaction", "kind": "rating"}],
    "cells": [
        {"id": "c1", "rowId": "r1", "stageId": "st1", "text": "Creates an account"},
        {"id": "c2", "rowId": "r1", "stageId": "st2", "text": "Connects their data"},
        {"id": "c3", "rowId": "r1", "stageId": "st3", "text": "Ships a first report"},
        {"id": "c4", "rowId": "r1", "stageId": "st4", "text": "Checks it every Monday"},
        {"id": "c5", "rowId": "r2", "stageId": "st1", "score": 1},
        {"id": "c6", "rowId": "r2", "stageId": "st2", "score": -1},
        {"id": "c7", "rowId": "r2", "stageId": "st3", "score": 2},
        {"id": "c8", "rowId": "r2", "stageId": "st4", "score": 1},
        {"id": "c9", "rowId": "r3", "stageId": "st1", "rating": 80},
        {"id": "c10", "rowId": "r3", "stageId": "st2", "rating": 40},
        {"id": "c11", "rowId": "r3", "stageId": "st3", "rating": 92},
        {"id": "c12", "rowId": "r3", "stageId": "st4", "rating": 85}],
    "narration": {
        "1": "Signing up is quick, and people feel good about it.",
        "2": "Setup is where it hurts: connecting data is the hardest moment.",
        "3": "Then the first report lands, and that is the moment of delight.",
        "4": "From there it becomes a weekly habit.",
        "__why2": "Most churn happens here, so this is the stage worth redesigning first."}})

# ---------------------------------------------------------------- processmap
EX["processmap"] = doc("processmap", grid("Purchase order process", "executive", [
    g({"id": "p1", "type": "start", "text": "Need identified"}, 0, 0),
    g({"id": "p2", "type": "document", "text": "Purchase request"}, 1, 0),
    g({"id": "p3", "type": "decision", "text": "Over budget limit?"}, 2, 0),
    g({"id": "p4", "type": "process", "text": "Director approval"}, 2, 1),
    g({"id": "p5", "type": "process", "text": "Issue purchase order"}, 3, 0),
    g({"id": "p6", "type": "database", "text": "ERP"}, 3, 1),
    g({"id": "p7", "type": "end", "text": "Goods received"}, 4, 0)],
    [{"id": "e1", "from": "p1", "to": "p2"}, {"id": "e2", "from": "p2", "to": "p3"},
     {"id": "e3", "from": "p3", "to": "p4", "label": "yes"}, {"id": "e4", "from": "p3", "to": "p5", "label": "no"},
     {"id": "e5", "from": "p4", "to": "p5"}, {"id": "e6", "from": "p5", "to": "p6", "style": "dashed"},
     {"id": "e7", "from": "p5", "to": "p7"}]))

# ---------------------------------------------------------------- decisiontree
EX["decisiontree"] = doc("decisiontree", grid("Should we launch now?", "editorial", [
    g({"id": "d", "type": "decision", "text": "Launch this quarter?"}, 0, 1),
    g({"id": "c", "type": "chance", "text": "Market response"}, 1, 0),
    g({"id": "h", "type": "outcome", "text": "Wait a quarter", "value": 50}, 1, 2),
    g({"id": "o1", "type": "outcome", "text": "Strong demand", "value": 500}, 2, 0),
    g({"id": "o2", "type": "outcome", "text": "Weak demand", "value": -200}, 2, 1)],
    [{"id": "e1", "from": "d", "to": "c", "label": "launch"},
     {"id": "e2", "from": "d", "to": "h", "label": "wait"},
     {"id": "e3", "from": "c", "to": "o1", "prob": 0.6},
     {"id": "e4", "from": "c", "to": "o2", "prob": 0.4}]))

# ---------------------------------------------------------------- architecture
arch_nodes = [
    {"id": "web", "type": "webapp", "text": "Web app", "x": 140, "y": 300},
    {"id": "cdn", "type": "cdn", "text": "CDN", "x": 140, "y": 140},
    {"id": "gw", "type": "apigateway", "text": "API gateway", "x": 380, "y": 300, "parentId": "grp"},
    {"id": "svc", "type": "service", "text": "Orders service", "x": 600, "y": 230, "parentId": "grp"},
    {"id": "auth", "type": "auth", "text": "Auth", "x": 600, "y": 380, "parentId": "grp"},
    {"id": "q", "type": "queue", "text": "Events queue", "x": 820, "y": 230, "parentId": "grp"},
    {"id": "db", "type": "database", "text": "Orders DB", "x": 820, "y": 380, "parentId": "grp"},
    {"id": "ai", "type": "ai", "text": "Fraud model", "x": 1120, "y": 230},
    {"id": "grp", "type": "group", "text": "Production VPC", "x": 640, "y": 300, "w": 760, "h": 400, "back": True}]
EX["architecture"] = doc("architecture", {
    "title": "Online store — production", "theme": "orbit",
    "nodes": arch_nodes,
    "edges": [{"id": "e1", "from": "cdn", "to": "web"},
              {"id": "e2", "from": "web", "to": "gw", "label": "HTTPS"},
              {"id": "e3", "from": "gw", "to": "svc"}, {"id": "e4", "from": "gw", "to": "auth"},
              {"id": "e5", "from": "svc", "to": "q", "anim": "flow"},
              {"id": "e6", "from": "svc", "to": "db"},
              {"id": "e7", "from": "q", "to": "ai", "label": "score order", "anim": "laser"}],
    "narration": {
        "1": "Customers reach the store through the web app.",
        "2": "Static files come from the CDN, close to wherever the customer is.",
        "3": "Every API call enters through one gateway.",
        "4": "The orders service does the real work.",
        "5": "Sign-in is handled by a separate auth service.",
        "6": "Each new order is published to an events queue.",
        "7": "And stored in the orders database.",
        "8": "A fraud model scores each order from the queue, outside the main path.",
        "9": "Everything inside this boundary runs in the production network.",
        "__why6": "The queue lets slow work like fraud scoring happen without making checkout wait."}})

# ---------------------------------------------------------------- dataflow
EX["dataflow"] = doc("dataflow", grid("Payroll — level 1", "quartz", [
    g({"id": "emp", "type": "entity", "text": "Employee"}, 0, 0),
    g({"id": "p1", "type": "dfProcess", "text": "Record hours"}, 1, 0),
    g({"id": "ts", "type": "datastore", "text": "Timesheets"}, 1, 1),
    g({"id": "p2", "type": "dfProcess", "text": "Calculate pay"}, 2, 1),
    g({"id": "bank", "type": "entity", "text": "Bank"}, 3, 1)],
    [{"id": "f1", "from": "emp", "to": "p1", "label": "hours worked"},
     {"id": "f2", "from": "p1", "to": "ts", "label": "timesheet"},
     {"id": "f3", "from": "ts", "to": "p2", "label": "approved hours"},
     {"id": "f4", "from": "p2", "to": "bank", "label": "payment file"}]))

# ---------------------------------------------------------------- network
EX["network"] = doc("network", grid("Small office network", "terminal", [
    g({"id": "inet", "type": "internet", "text": "Internet"}, 1, 0),
    g({"id": "fw", "type": "firewall", "text": "Firewall"}, 1, 1),
    g({"id": "rt", "type": "router", "text": "Router"}, 1, 2),
    g({"id": "sw", "type": "switch", "text": "Switch"}, 1, 3),
    g({"id": "wifi", "type": "wifi", "text": "Wi-Fi"}, 0, 3),
    g({"id": "srv", "type": "server", "text": "File server"}, 2, 3),
    g({"id": "pc", "type": "workstation", "text": "Desks x12"}, 1, 4),
    g({"id": "lap", "type": "mobile", "text": "Laptops"}, 0, 4)],
    [{"id": "l1", "from": "inet", "to": "fw", "kind": "fiber"},
     {"id": "l2", "from": "fw", "to": "rt"}, {"id": "l3", "from": "rt", "to": "sw"},
     {"id": "l4", "from": "sw", "to": "wifi"}, {"id": "l5", "from": "sw", "to": "srv"},
     {"id": "l6", "from": "sw", "to": "pc"}, {"id": "l7", "from": "wifi", "to": "lap", "kind": "wireless"}]))

# ---------------------------------------------------------------- fishbone
EX["fishbone"] = doc("fishbone", grid("Why deliveries arrive late", "marker", [
    g({"id": "ef", "type": "effect", "text": "Late deliveries"}, 4, 1),
    g({"id": "k1", "type": "category", "text": "People"}, 1, 0),
    g({"id": "k2", "type": "category", "text": "Process"}, 3, 0),
    g({"id": "k3", "type": "category", "text": "Vehicles"}, 1, 2),
    g({"id": "k4", "type": "category", "text": "Suppliers"}, 3, 2),
    g({"id": "c1", "type": "cause", "text": "Understaffed weekends"}, 0, 0),
    g({"id": "c2", "type": "cause", "text": "Old trucks"}, 0, 2),
    g({"id": "c3", "type": "cause", "text": "Manual routing"}, 2, 0),
    g({"id": "c4", "type": "cause", "text": "Late raw stock"}, 2, 2)],
    [{"id": "b1", "from": "k1", "to": "ef"}, {"id": "b2", "from": "k2", "to": "ef"},
     {"id": "b3", "from": "k3", "to": "ef"}, {"id": "b4", "from": "k4", "to": "ef"},
     {"id": "b5", "from": "c1", "to": "k1"}, {"id": "b6", "from": "c2", "to": "k3"},
     {"id": "b7", "from": "c3", "to": "k2"}, {"id": "b8", "from": "c4", "to": "k4"}]))

# ---------------------------------------------------------------- usecase
EX["usecase"] = doc("usecase", {
    "title": "Library app", "theme": "canvas",
    "nodes": [
        {"id": "m", "type": "actor", "text": "Member", "x": 160, "y": 220},
        {"id": "l", "type": "actor", "text": "Librarian", "x": 880, "y": 380},
        {"id": "u1", "type": "usecase", "text": "Search catalogue", "x": 520, "y": 150},
        {"id": "u2", "type": "usecase", "text": "Borrow a book", "x": 520, "y": 260},
        {"id": "u3", "type": "usecase", "text": "Sign in", "x": 520, "y": 370},
        {"id": "u4", "type": "usecase", "text": "Add a book", "x": 520, "y": 470},
        {"id": "sys", "type": "boundary", "text": "Library app", "x": 520, "y": 310, "w": 420, "h": 460, "back": True}],
    "edges": [{"id": "e1", "from": "m", "to": "u1"}, {"id": "e2", "from": "m", "to": "u2"},
              {"id": "e3", "from": "u2", "to": "u3", "kind": "include", "label": "«include»"},
              {"id": "e4", "from": "l", "to": "u4"}, {"id": "e5", "from": "l", "to": "u3"}]})

# ---------------------------------------------------------------- threatmodel
EX["threatmodel"] = doc("threatmodel", {
    "title": "Login service — STRIDE", "theme": "obsidian",
    "nodes": [
        {"id": "u", "type": "actor", "text": "User", "x": 200, "y": 300},
        {"id": "web", "type": "dfProcess", "text": "Login API", "x": 620, "y": 300,
         "threats": [{"id": "t1", "stride": "S", "sev": "high", "title": "Credential stuffing",
                      "mitigation": "Rate limits and breached-password checks"}]},
        {"id": "db", "type": "datastore", "text": "Users DB", "x": 900, "y": 300,
         "threats": [{"id": "t2", "stride": "I", "sev": "critical", "title": "Hash dump",
                      "mitigation": "Argon2id hashes, encrypted at rest"}]},
        {"id": "tb", "type": "trustBoundary", "text": "Data centre", "x": 760, "y": 310, "w": 560, "h": 340, "back": True}],
    "edges": [{"id": "f1", "from": "u", "to": "web", "label": "email + password"},
              {"id": "f2", "from": "web", "to": "db", "label": "lookup"},
              {"id": "a1", "from": "u", "to": "db", "label": "SQL injection attempt", "attack": True}]})

# ---------------------------------------------------------------- c4model
EX["c4model"] = doc("c4model", grid("Internet banking — containers", "linear", [
    g({"id": "p", "type": "person", "text": "Customer"}, 0, 0),
    g({"id": "w", "type": "container", "text": "Web app", "tech": "React"}, 1, 0),
    g({"id": "a", "type": "container", "text": "API", "tech": "Spring Boot"}, 2, 0),
    g({"id": "d", "type": "database", "text": "Accounts DB", "tech": "PostgreSQL"}, 2, 1),
    g({"id": "x", "type": "externalSystem", "text": "Core banking"}, 3, 0)],
    [{"id": "e1", "from": "p", "to": "w", "label": "Uses"},
     {"id": "e2", "from": "w", "to": "a", "label": "JSON / HTTPS"},
     {"id": "e3", "from": "a", "to": "d", "label": "Reads and writes"},
     {"id": "e4", "from": "a", "to": "x", "label": "Calls", "anim": "flow"}]))

# ---------------------------------------------------------------- conceptmap
EX["conceptmap"] = doc("conceptmap", grid("Photosynthesis", "forest", [
    g({"id": "c1", "type": "concept", "text": "Plants"}, 1, 0),
    g({"id": "c2", "type": "concept", "text": "Sunlight"}, 0, 1),
    g({"id": "c3", "type": "concept", "text": "Glucose"}, 1, 2),
    g({"id": "c4", "type": "subtopic", "text": "Chlorophyll"}, 2, 1),
    g({"id": "c5", "type": "ellipse", "text": "Oak leaf"}, 2, 0)],
    [{"id": "r1", "from": "c1", "to": "c2", "label": "capture"},
     {"id": "r2", "from": "c1", "to": "c3", "label": "make"},
     {"id": "r3", "from": "c1", "to": "c4", "label": "contain"},
     {"id": "r4", "from": "c5", "to": "c1", "label": "is part of"}],
    focusQuestion="How do plants make food?"))

# ---------------------------------------------------------------- umlclass
EX["umlclass"] = doc("umlclass", grid("Ordering domain", "quartz", [
    g({"id": "c1", "type": "umlClass", "text": "Customer\n--\n+ id: UUID\n+ name: String\n--\n+ placeOrder(): Order"}, 0, 0),
    g({"id": "c2", "type": "umlClass", "text": "Order\n--\n+ id: UUID\n+ total: Money\n--\n+ pay(): void"}, 1, 0),
    g({"id": "c3", "type": "umlClass", "text": "OrderLine\n--\n+ qty: int\n+ price: Money"}, 2, 0),
    g({"id": "c4", "type": "umlClass", "text": "VipCustomer\n--\n+ tier: int"}, 0, 1.5)],
    [{"id": "r1", "from": "c1", "to": "c2", "kind": "assoc", "label": "places"},
     {"id": "r2", "from": "c2", "to": "c3", "kind": "compose"},
     {"id": "r3", "from": "c4", "to": "c1", "kind": "inherit"}]))

# ---------------------------------------------------------------- erdiagram
EX["erdiagram"] = doc("erdiagram", grid("Shop schema", "drafting", [
    g({"id": "t1", "type": "erEntity", "text": "customers\n--\nPK id\nname\nemail"}, 0, 0),
    g({"id": "t2", "type": "erEntity", "text": "orders\n--\nPK id\nFK customer_id\ncreated_at"}, 1, 0),
    g({"id": "t3", "type": "erEntity", "text": "order_items\n--\nPK id\nFK order_id\nFK product_id\nqty"}, 2, 0),
    g({"id": "t4", "type": "erEntity", "text": "products\n--\nPK id\nname\nprice"}, 2, 1.5)],
    [{"id": "r1", "from": "t1", "to": "t2", "kind": "oneToMany", "label": "places"},
     {"id": "r2", "from": "t2", "to": "t3", "kind": "oneToMany", "label": "contains"},
     {"id": "r3", "from": "t4", "to": "t3", "kind": "oneToMany", "label": "appears in"}]))

# ---------------------------------------------------------------- bpmn
bp = [
    {"id": "s", "type": "bpmnStart", "text": "Leave requested", "x": 140, "y": 190, "parentId": "pool"},
    {"id": "t", "type": "userTask", "text": "Manager reviews", "x": 300, "y": 190, "parentId": "pool"},
    {"id": "g", "type": "bpmnGwX", "text": "Approved?", "x": 470, "y": 190, "parentId": "pool"},
    {"id": "t2", "type": "serviceTask", "text": "Book leave", "x": 650, "y": 190, "parentId": "pool"},
    {"id": "en", "type": "bpmnEnd", "text": "Done", "x": 850, "y": 190, "parentId": "pool"},
    {"id": "er", "type": "sendTask", "text": "Notify refusal", "x": 650, "y": 310, "parentId": "pool"},
    {"id": "pool", "type": "boundary", "text": "HR", "x": 520, "y": 250, "w": 900, "h": 300, "back": True}]
EX["bpmn"] = doc("bpmn", {
    "title": "Leave request", "theme": "quartz", "nodes": bp,
    "edges": [{"id": "f1", "from": "s", "to": "t"}, {"id": "f2", "from": "t", "to": "g"},
              {"id": "f3", "from": "g", "to": "t2", "label": "yes"}, {"id": "f4", "from": "t2", "to": "en"},
              {"id": "f5", "from": "g", "to": "er", "label": "no"}, {"id": "f6", "from": "er", "to": "en"}],
    })

# ---------------------------------------------------------------- visuallearning
EX["visuallearning"] = doc("visuallearning", grid("How HTTPS keeps you safe", "drawingbook", [
    g({"id": "s1", "type": "spotcard", "text": "The handshake", "blocks": [
        {"k": "text", "text": "Before any data moves, your browser and the server agree on secret keys."},
        {"k": "bullets", "text": "Browser says hello\nServer shows its certificate\nThey agree on a session key", "marker": "num"}]}, 0, 0),
    g({"id": "s2", "type": "spotcard", "text": "Sealed traffic", "blocks": [
        {"k": "text", "text": "Every request and reply is now encrypted with that session key."},
        {"k": "diagram", "text": "Browser -> Server\nServer -> Browser"}]}, 1, 0),
    g({"id": "s3", "type": "spotcard", "text": "Why trust the certificate?", "blocks": [
        {"k": "text", "text": "A certificate authority your browser already trusts has vouched for the server."}]}, 2, 0)],
    [{"id": "e1", "from": "s1", "to": "s2"}, {"id": "e2", "from": "s2", "to": "s3"}],
    narration={
        "1": "First comes the handshake. Your browser and the server agree on secret keys before anything else moves.",
        "2": "From then on, every request and every reply is sealed with that session key.",
        "3": "But why believe the server is who it says it is? Because someone your browser already trusts has vouched for it."}))

# ---------------------------------------------------------------- visualstory
EX["visualstory"] = doc("visualstory", {
    "type": "visual-story", "schemaVersion": 1, "title": "Why we recycle glass", "theme": "quartz",
    "sceneOrder": ["s1", "s2"],
    "scenes": [
        {"id": "s1", "title": "The problem", "aspectRatio": "16:9",
         "objects": [
             {"id": "o1", "type": "text", "x": 120, "y": 90, "width": 1040, "height": 90,
              "text": "A glass bottle takes a million years to break down", "style": {"fontSize": 44}},
             {"id": "o2", "type": "shape", "shape": "rounded", "x": 160, "y": 300, "width": 360, "height": 160,
              "text": "Landfill", "initialVisibility": False},
             {"id": "o3", "type": "shape", "shape": "rounded", "x": 760, "y": 300, "width": 360, "height": 160,
              "text": "Recycling plant", "initialVisibility": False},
             {"id": "o4", "type": "connector", "fromObjectId": "o2", "toObjectId": "o3", "initialVisibility": False}],
         "steps": [
             {"id": "st1", "title": "Landfill", "narration": {"text": "Thrown away, a bottle sits in landfill almost forever."},
              "actions": [{"id": "a1", "objectId": "o2", "type": "appear"}]},
             {"id": "st2", "title": "Recycling", "narration": {"text": "Recycled, it can be melted down and made again."},
              "actions": [{"id": "a2", "objectId": "o3", "type": "appear"},
                          {"id": "a3", "objectId": "o4", "type": "draw-connector"}]}]},
        {"id": "s2", "title": "The payoff", "aspectRatio": "16:9",
         "objects": [
             {"id": "o5", "type": "bullets", "x": 160, "y": 160, "width": 960, "height": 360,
              "items": ["Endlessly recyclable", "Saves energy over new glass", "Keeps sand in the ground"],
              "initialVisibility": False}],
         "steps": [
             {"id": "st3", "title": "Why it matters", "narration": {"text": "And unlike plastic, glass can be recycled again and again."},
              "actions": [{"id": "a4", "objectId": "o5", "type": "reveal-text"}]}]}]})

for mode, d in EX.items():
    (OUT / (mode + ".json")).write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", len(EX), "examples to", OUT)
