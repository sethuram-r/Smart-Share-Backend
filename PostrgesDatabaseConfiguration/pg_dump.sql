--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 11.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: access_management; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA access_management;


ALTER SCHEMA access_management OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: access_request; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management.access_request
(
    id                integer NOT NULL,
    file              text,
    owner_of_file     text,
    user_name         text,
    access_type       text,
    status_of_request text
);


ALTER TABLE access_management.access_request
    OWNER TO postgres;

--
-- Name: file; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management.file
(
    id       integer NOT NULL,
    name     text,
    owner_id integer
);


ALTER TABLE access_management.file
    OWNER TO postgres;

--
-- Name: file_id_seq; Type: SEQUENCE; Schema: access_management; Owner: postgres
--

CREATE SEQUENCE access_management.file_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE access_management.file_id_seq
    OWNER TO postgres;

--
-- Name: file_id_seq; Type: SEQUENCE OWNED BY; Schema: access_management; Owner: postgres
--

ALTER SEQUENCE access_management.file_id_seq OWNED BY access_management.file.id;


--
-- Name: file_user_access; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management.file_user_access
(
    file_id   integer NOT NULL,
    user_id   integer NOT NULL,
    access_id integer
);


ALTER TABLE access_management.file_user_access
    OWNER TO postgres;

--
-- Name: owner; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management.owner
(
    id   integer NOT NULL,
    name text
);


ALTER TABLE access_management.owner
    OWNER TO postgres;

--
-- Name: owner_id_seq; Type: SEQUENCE; Schema: access_management; Owner: postgres
--

CREATE SEQUENCE access_management.owner_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE access_management.owner_id_seq
    OWNER TO postgres;

--
-- Name: owner_id_seq; Type: SEQUENCE OWNED BY; Schema: access_management; Owner: postgres
--

ALTER SEQUENCE access_management.owner_id_seq OWNED BY access_management.owner.id;


--
-- Name: permissions_assigned; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management.permissions_assigned
(
    id     integer NOT NULL,
    read   boolean,
    write  boolean,
    delete boolean
);


ALTER TABLE access_management.permissions_assigned
    OWNER TO postgres;

--
-- Name: permissions_assigned_id_seq; Type: SEQUENCE; Schema: access_management; Owner: postgres
--

CREATE SEQUENCE access_management.permissions_assigned_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE access_management.permissions_assigned_id_seq
    OWNER TO postgres;

--
-- Name: permissions_assigned_id_seq; Type: SEQUENCE OWNED BY; Schema: access_management; Owner: postgres
--

ALTER SEQUENCE access_management.permissions_assigned_id_seq OWNED BY access_management.permissions_assigned.id;


--
-- Name: user; Type: TABLE; Schema: access_management; Owner: postgres
--

CREATE TABLE access_management."user"
(
    id   integer NOT NULL,
    name text
);


ALTER TABLE access_management."user"
    OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: access_management; Owner: postgres
--

CREATE SEQUENCE access_management.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE access_management.user_id_seq
    OWNER TO postgres;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: access_management; Owner: postgres
--

ALTER SEQUENCE access_management.user_id_seq OWNED BY access_management."user".id;


--
-- Name: file id; Type: DEFAULT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file
    ALTER COLUMN id SET DEFAULT nextval('access_management.file_id_seq'::regclass);


--
-- Name: owner id; Type: DEFAULT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.owner
    ALTER COLUMN id SET DEFAULT nextval('access_management.owner_id_seq'::regclass);


--
-- Name: permissions_assigned id; Type: DEFAULT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.permissions_assigned
    ALTER COLUMN id SET DEFAULT nextval('access_management.permissions_assigned_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management."user"
    ALTER COLUMN id SET DEFAULT nextval('access_management.user_id_seq'::regclass);


--
-- Name: access_request access_request_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.access_request
    ADD CONSTRAINT access_request_pkey PRIMARY KEY (id);


--
-- Name: file file_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file
    ADD CONSTRAINT file_pkey PRIMARY KEY (id);


--
-- Name: file_user_access file_user_access_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file_user_access
    ADD CONSTRAINT file_user_access_pkey PRIMARY KEY (file_id, user_id);


--
-- Name: owner owner_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.owner
    ADD CONSTRAINT owner_pkey PRIMARY KEY (id);


--
-- Name: permissions_assigned permissions_assigned_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.permissions_assigned
    ADD CONSTRAINT permissions_assigned_pkey PRIMARY KEY (id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.user
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: file file_owner_id_fkey; Type: FK CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file
    ADD CONSTRAINT file_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES access_management.owner (id);


--
-- Name: file_user_access file_user_access_access_id_fkey; Type: FK CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file_user_access
    ADD CONSTRAINT file_user_access_access_id_fkey FOREIGN KEY (access_id) REFERENCES access_management.permissions_assigned (id);


--
-- Name: file_user_access file_user_access_file_id_fkey; Type: FK CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file_user_access
    ADD CONSTRAINT file_user_access_file_id_fkey FOREIGN KEY (file_id) REFERENCES access_management.file (id);


--
-- Name: file_user_access file_user_access_user_id_fkey; Type: FK CONSTRAINT; Schema: access_management; Owner: postgres
--

ALTER TABLE ONLY access_management.file_user_access
    ADD CONSTRAINT file_user_access_user_id_fkey FOREIGN KEY (user_id) REFERENCES access_management.user (id);


--

INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (1, true, true, true);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (2, false, true, true);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (3, true, false, true);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (4, true, true, false);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (5, false, false, true);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (6, true, false, false);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (7, false, true, false);
INSERT INTO access_management.permissions_assigned (id, read, write, delete)
VALUES (8, false, false, false);


--
-- PostgreSQL database dump complete
--

