"use client";

import { useEffect, useState } from "react";

import DepartmentCard from "@/components/knowledge/department-card";

import DocumentTable from "@/components/knowledge/document-table";

import UploadDocumentDialog from "@/components/knowledge/upload-document-dialog";

import { getDepartments } from "@/services/department-service";

import { getDocuments } from "@/services/document-service";

import { Department } from "@/types/department";

import { Document } from "@/types/document";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function KnowledgeBasePage() {
  const [departments, setDepartments] =
    useState<Department[]>([]);

  const [documents, setDocuments] =
    useState<Document[]>([]);

  const [selectedDepartment, setSelectedDepartment] =
    useState("all");

  const filteredDocuments =
    selectedDepartment === "all"
      ? documents
      : documents.filter(
        (doc) =>
          doc.department_id ===
          selectedDepartment
      );

  async function loadData() {
    try {
      const [
        departmentData,
        documentData,
      ] = await Promise.all([
        getDepartments(),
        getDocuments(),
      ]);

      setDepartments(
        departmentData
      );

      setDocuments(
        documentData
      );
    } catch (error) {
      console.error(
        "Failed loading KB data",
        error
      );
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      <div className="flex justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Knowledge Base
          </h1>

          <p className="text-muted-foreground">
            Manage documents and
            departments
          </p>
        </div>

        <UploadDocumentDialog
          departments={departments}
          onUploaded={loadData}
        />
      </div>

      <section>
        <h2 className="text-xl font-semibold mb-4">
          Departments
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {departments.map((dept) => (
            <DepartmentCard
              key={dept.id}
              name={
                dept.display_name
              }
              count={
                dept.document_count
              }
            />
          ))}
        </div>
      </section>

      <section>
        <div className="flex justify-between mb-4">
          <h2 className="text-xl font-semibold">
            Documents
          </h2>

          <Select
            value={selectedDepartment}
            onValueChange={
              setSelectedDepartment
            }
          >
            <SelectTrigger className="w-64">
              <SelectValue
                placeholder="Filter Department"
              />
            </SelectTrigger>

            <SelectContent>
              <SelectItem value="all">
                All Departments
              </SelectItem>

              {departments.map((dept) => (
                <SelectItem
                  key={dept.id}
                  value={dept.id}
                >
                  {dept.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <DocumentTable
          documents={filteredDocuments}
        />
      </section>
    </div>
  );
}