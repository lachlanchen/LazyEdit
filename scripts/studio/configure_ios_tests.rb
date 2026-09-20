#!/usr/bin/env ruby
# Run once on the Mac if the shared StudioNative scheme/test target is absent.
require 'xcodeproj'
path = ARGV.fetch(0)
project = Xcodeproj::Project.open(path)
app = project.targets.find { |t| t.name == 'App' }
test = project.targets.find { |t| t.name == 'StudioUITests' }
unless test
  test = project.new_target(:ui_test_bundle, 'StudioUITests', :ios, '16.0')
  test.add_dependency(app)
  group = project.main_group.new_group('StudioUITests', 'StudioUITests')
  test.source_build_phase.add_file_reference(group.new_file('StudioUITests.swift'))
  test.build_configurations.each do |config|
    config.build_settings.update({
      'GENERATE_INFOPLIST_FILE' => 'YES', 'PRODUCT_NAME' => 'StudioUITests', 'SWIFT_VERSION' => '5.0',
      'PRODUCT_BUNDLE_IDENTIFIER' => 'art.lazying.lazyedit.uitests',
      'TEST_TARGET_NAME' => 'App', 'CODE_SIGNING_ALLOWED' => 'NO',
      'TARGETED_DEVICE_FAMILY' => '1,2'
    })
  end
  project.save
end
scheme = Xcodeproj::XCScheme.new
scheme.add_build_target(app)
scheme.add_test_target(test)
scheme.set_launch_target(app)
scheme.save_as(path, 'StudioNative', true)
