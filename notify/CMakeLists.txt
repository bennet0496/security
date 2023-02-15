CMAKE_MINIMUM_REQUIRED(VERSION 3.21)
PROJECT(telegram-send LANGUAGES C VERSION 0.1.0)


set(CMAKE_C_STANDARD 23)

add_executable(telegram-send src/main.c)

INCLUDE_DIRECTORIES(include ${CMAKE_SOURCE_DIR}/../lib/telebot/include)
LINK_DIRECTORIES(BEFORE "${CMAKE_SOURCE_DIR}/lib")


find_library(TB telebot HINTS ${CMAKE_SOURCE_DIR}/lib REQUIRED)

target_link_libraries(telegram-send ${TB} pthread)