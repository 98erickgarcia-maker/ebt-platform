FROM node:24-bookworm-slim AS frontend
WORKDIR /work/src/frontend
COPY src/frontend/package*.json ./
RUN npm ci
COPY src/frontend/ ./
RUN npm run build

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS backend
WORKDIR /work
ENV MSBuildEnableWorkloadResolver=false
COPY src/backend/Ebt.Platform.Api/ src/backend/Ebt.Platform.Api/
RUN dotnet restore src/backend/Ebt.Platform.Api --locked-mode
COPY --from=frontend /work/src/backend/Ebt.Platform.Api/wwwroot/ src/backend/Ebt.Platform.Api/wwwroot/
RUN dotnet publish src/backend/Ebt.Platform.Api --no-restore -c Release -o /out /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=backend /out/ ./
ENV ASPNETCORE_HTTP_PORTS=8080 ASPNETCORE_ENVIRONMENT=Production
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet", "Ebt.Platform.Api.dll"]
