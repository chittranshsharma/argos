"use client";

import { useEffect, useState } from "react";
import { getAllReports, clearReports, getCompanies } from "@/lib/api";
import type { Report, Company } from "@/lib/types";
import { FileText, Download, Eye, ExternalLink, Trash2 } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";