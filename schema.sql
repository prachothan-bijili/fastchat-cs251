--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Ubuntu 15.1-1.pgdg22.04+1)
-- Dumped by pg_dump version 15.1 (Ubuntu 15.1-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: grp; Type: TABLE; Schema: public; Owner: fastchat
--

CREATE TABLE public.grp (
    id character varying(8) NOT NULL,
    name character varying(20) NOT NULL,
    admin_id character varying(8) NOT NULL
);


ALTER TABLE public.grp OWNER TO fastchat;

--
-- Name: grp_memb; Type: TABLE; Schema: public; Owner: fastchat
--

CREATE TABLE public.grp_memb (
    member_id character varying(8) NOT NULL,
    group_id character varying(8) NOT NULL,
    is_known boolean
);


ALTER TABLE public.grp_memb OWNER TO fastchat;

--
-- Name: msg; Type: TABLE; Schema: public; Owner: fastchat
--

CREATE TABLE public.msg (
    message text,
    is_read boolean,
    is_group boolean,
    group_id character varying(8),
    sender_id character varying(8),
    receiver_id character varying(8),
    "time" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.msg OWNER TO fastchat;

--
-- Name: users; Type: TABLE; Schema: public; Owner: fastchat
--

CREATE TABLE public.users (
    id character varying(8) NOT NULL,
    name character varying(20) NOT NULL,
    password character varying(100) NOT NULL,
    public_key character varying(1024) NOT NULL,
    status boolean
);


ALTER TABLE public.users OWNER TO fastchat;

--
-- Name: grp grp_pkey; Type: CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_pkey PRIMARY KEY (id);


--
-- Name: users users_name_key; Type: CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_name_key UNIQUE (name);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: grp grp_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.grp
    ADD CONSTRAINT grp_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: grp_memb grp_memb_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.grp_memb
    ADD CONSTRAINT grp_memb_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.grp(id);


--
-- Name: grp_memb grp_memb_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.grp_memb
    ADD CONSTRAINT grp_memb_member_id_fkey FOREIGN KEY (member_id) REFERENCES public.users(id);


--
-- Name: msg msg_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.msg
    ADD CONSTRAINT msg_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES public.users(id);


--
-- Name: msg msg_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: fastchat
--

ALTER TABLE ONLY public.msg
    ADD CONSTRAINT msg_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

