"use client";

import { Search, Bell, User, X, Check, Info, LogOut } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/utils/supabase/client";